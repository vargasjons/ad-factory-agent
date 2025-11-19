"""Video generation tool supporting both Sora (OpenAI) and Veo (Google Gemini) models."""

from typing import Literal, Optional
import asyncio

from openai import OpenAI
from pydantic import Field, field_validator

from agency_swarm import BaseTool

from ugc_agent.tools.utils.video_utils import (
    SORA_MODEL,
    ensure_not_blank,
    get_openai_client,
    get_gemini_client,
    is_veo_model,
    is_sora_model,
    resolve_input_reference,
    validate_resolution,
    save_video_with_metadata,
    save_veo_video_with_metadata,
)


class GenerateVideo(BaseTool):
    """
    Generates a video using either OpenAI's Sora or Google's Veo model.

    Tool is stateless, and does not maintain any charahcters / scenes / etc between calls. It does not support variables like [INTERNAL PROMPT] in the prompt.

    **Important**: Sora 2 and Sora 2 Pro do not support reference images with faces.
    
    Videos are saved to: mnt/{product_name}/generated_videos/
    """
    product_name: str = Field(
        ...,
        description="Name of the product this video is for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract'). Used to organize files into product-specific folders.",
    )
    prompt: str = Field(
        ...,
        description=(
            "Detailed marketing description of the desired video. Include subjects, "
            "camera motion, lighting, and mood for the video generation model. "
            "Be ware that sometimes including things you DONT want to display in the video "
            "can cause the model to generate them instead. Simply don't mention what you don't want to see in the prompt."
        ),
    )
    name: str = Field(
        ...,
        description="The name for the generated video file (without extension)",
    )
    seconds: Literal["4", "8", "12"] = Field(
        default="8",
        description="Clip length in seconds. Sora currently supports clips up to 12 seconds. Use 8 second for shorter clips like b rolls and 12 seconds for longer scripts that contain multiple sentences.",
    )
    input_reference: Optional[str] = Field(
        default=None,
        description=(
            "Optional reference image to guide the generation. Can be: "
            "1) Image name without extension (searches generated_images and generated_videos folders), "
            "2) Full local path, or 3) HTTPS URL."
        ),
    )
    size: Literal['720x1280', '1280x720', '1024x1792', '1792x1024'] = Field(
        default='1280x720',
        description="Optional resolution in WIDTHxHEIGHT format (e.g. 1280x720). For Sora: exact resolution. For Veo: reference image will be cropped/resized to match this aspect ratio to prevent stretching.",
    )

    @field_validator("prompt")
    @classmethod
    def _prompt_not_blank(cls, value: str) -> str:
        return ensure_not_blank(value, "prompt")

    @field_validator("input_reference")
    @classmethod
    def _reference_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            ensure_not_blank(value, "input_reference")
        return value

    @field_validator("size")
    @classmethod
    def _size_format(cls, value: Optional[str]) -> Optional[str]:
        return validate_resolution(value)

    async def run(self) -> dict:
        """Generate a marketing video (Sora by default)."""
        
        # Get model configuration from onboarding config
        try:
            from onboarding_config import config
        except ImportError:
            config = {}
            print("Warning: onboarding_config not found, using defaults.")
        
        sora_model = config.get("sora_model", SORA_MODEL)
        veo_model = config.get("veo_model")

        selected_model = sora_model

        if is_sora_model(selected_model):
            return await self._generate_with_sora(selected_model)

        if is_veo_model(selected_model):
            return await self._generate_with_veo(selected_model)

        if veo_model and is_veo_model(veo_model):
            return await self._generate_with_veo(veo_model)

        if is_sora_model(SORA_MODEL):
            return await self._generate_with_sora(SORA_MODEL)

        raise ValueError(f"Unable to determine a valid video model (sora_model={sora_model}, veo_model={veo_model}).")

    async def _generate_with_sora(self, model: str) -> dict:
        """Generate video using OpenAI's Sora API."""
        
        client: OpenAI = get_openai_client()
        reference_file = None
        
        try:
            # Resolve and resize reference image to match video dimensions
            reference_file = resolve_input_reference(
                self.input_reference, 
                target_size=self.size if self.input_reference else None,
                product_name=self.product_name
            )

            request_payload = {
                "prompt": self.prompt,
                "model": model,
                "seconds": self.seconds,
            }
            if self.size:
                request_payload["size"] = self.size
            if reference_file is not None:
                request_payload["input_reference"] = reference_file

            print(f"Submitting video generation request to Sora ({model})...")
            
            # Run blocking operation in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            video = await loop.run_in_executor(
                None, 
                lambda: client.videos.create_and_poll(**request_payload)
            )
            print(f"Video generation status: {video.status}")

            # Save the generated video with all metadata
            output = save_video_with_metadata(client, video.id, self.name, self.product_name)

            return output

        finally:
            if reference_file is not None and hasattr(reference_file, "close"):
                try:
                    reference_file.close()
                except Exception:
                    pass

    async def _generate_with_veo(self, model: str) -> dict:
        """Generate video using Google's Veo API with optional reference image."""
        
        from google.genai.types import GenerateVideosConfig, Image, VideoGenerationReferenceImage
        
        client = get_gemini_client()
        
        try:
            # Prepare config
            config_kwargs = {}
            
            # Add aspect_ratio only when NOT using reference images
            # (aspect_ratio parameter causes "not supported" error when used with reference images)
            if self.size and not self.input_reference:
                width, height = map(int, self.size.split('x'))
                if width < height:
                    aspect_ratio = "9:16"  # Portrait
                else:
                    aspect_ratio = "16:9"  # Landscape
                config_kwargs["aspect_ratio"] = aspect_ratio
            
            if self.input_reference:
                # Load the reference image
                from ugc_agent.tools.utils.image_utils import load_image_by_name, get_images_dir
                from pathlib import Path
                from urllib.parse import urlparse
                
                parsed = urlparse(self.input_reference)
                
                if parsed.scheme in ("http", "https"):
                    raise ValueError("Veo does not support URL reference images. Please use local images.")
                else:
                    # Try as full path first
                    path = Path(self.input_reference).expanduser().resolve()
                    
                    if path.exists():
                        image_path = str(path)
                    else:
                        # Get product-specific images directory
                        images_dir = get_images_dir(self.product_name)
                        
                        # Try as image name without extension
                        pil_image, image_path, load_error = load_image_by_name(
                            self.input_reference, images_dir, [".png", ".jpg", ".jpeg", ".webp"]
                        )
                        if load_error:
                            raise FileNotFoundError(f"Reference image '{self.input_reference}' not found in {images_dir}")
                
                print(f"Loading reference image for Veo: {image_path}")
                
                # Load and resize image to match target aspect ratio
                from PIL import Image as PILImage
                from io import BytesIO
                
                with PILImage.open(image_path) as img:
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # If size is specified, resize to match target aspect ratio using crop
                    if self.size:
                        target_width, target_height = map(int, self.size.split('x'))
                        
                        # Calculate target aspect ratio
                        target_ratio = target_width / target_height
                        img_ratio = img.width / img.height
                        
                        # Crop to match aspect ratio (center crop)
                        if img_ratio > target_ratio:
                            # Image is wider, crop width
                            new_width = int(img.height * target_ratio)
                            left = (img.width - new_width) // 2
                            img = img.crop((left, 0, left + new_width, img.height))
                        elif img_ratio < target_ratio:
                            # Image is taller, crop height
                            new_height = int(img.width / target_ratio)
                            top = (img.height - new_height) // 2
                            img = img.crop((0, top, img.width, top + new_height))
                        
                        # Resize to target dimensions
                        img = img.resize((target_width, target_height), PILImage.Resampling.LANCZOS)
                    
                    # Convert to bytes
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    image_bytes = buffer.getvalue()
                    mime_type = "image/png"
                
                # Add reference images to config
                config_kwargs["reference_images"] = [
                    VideoGenerationReferenceImage(
                        image=Image(
                            image_bytes=image_bytes,
                            mime_type=mime_type,
                        ),
                        reference_type="asset",
                    ),
                ]
            
            # Create config with all parameters
            config = GenerateVideosConfig(**config_kwargs)
            
            if self.size and self.input_reference:
                print(f"Submitting video generation request to Veo ({model}) - reference image resized to {self.size} (aspect ratio inferred from image)...")
            elif self.size:
                print(f"Submitting video generation request to Veo ({model}) - size: {self.size}...")
            else:
                print(f"Submitting video generation request to Veo ({model})...")
            
            # Run blocking operation in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: client.models.generate_videos(
                    model=model,
                    prompt=self.prompt,
                    config=config,
                )
            )
            
            # Poll the operation status until the video is ready
            while not operation.done:
                print("Waiting for Veo video generation to complete...")
                await asyncio.sleep(10)
                operation = await loop.run_in_executor(
                    None,
                    lambda: client.operations.get(operation)
                )
            
            print("Video generation complete!")
            
            # Download the generated video
            generated_video = operation.response.generated_videos[0]
            output = save_veo_video_with_metadata(client, generated_video.video, self.name, self.product_name)
            
            return output
            
        except Exception as e:
            raise RuntimeError(f"Veo video generation failed: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    # Basic test invocation (Sora)
    tool = GenerateVideo(
        product_name="Test_Product",
        prompt=(
            "A selfie-style iPhone 15 Pro front-camera vertical video featuring a 35-year-old white male. He speaks in an encouraging tone."
        ),
        seconds="4",
        size="720x1280",
        name="test_video_sora",
        input_reference=None,
    )
    try:
        result = asyncio.run(tool.run())
        print(result)
    except Exception as exc:
        print(f"Video generation failed: {exc}")
