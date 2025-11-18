"""Video generation tool supporting both Sora (OpenAI) and Veo (Google Gemini) models."""

from typing import Literal, Optional
import time

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
    Supports Sora models (sora-2, sora-2-pro) and Veo models (veo-3.1, veo-3.0 variants).
    
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
            "camera motion, lighting, and mood for the video generation model."
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
        description="Optional resolution in WIDTHxHEIGHT format (e.g. 1280x720).",
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

    def run(self) -> dict:
        """Generate a marketing video using either Sora (OpenAI) or Veo (Google Gemini)."""
        
        # Get the video model from onboarding config
        try:
            from onboarding_config import config
            model = config.get("video_generation_model", SORA_MODEL)
        except ImportError:
            # Fallback to default if config not available
            model = SORA_MODEL
            print(f"Warning: onboarding_config not found, using default model: {model}")

        # Determine which model to use
        if is_sora_model(model):
            return self._generate_with_sora(model)
        elif is_veo_model(model):
            return self._generate_with_veo(model)
        else:
            raise ValueError(f"Unknown video model: {model}. Must be a Sora or Veo model.")

    def _generate_with_sora(self, model: str) -> dict:
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
            video = client.videos.create_and_poll(**request_payload)
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

    def _generate_with_veo(self, model: str) -> dict:
        """Generate video using Google's Veo API with optional reference image."""
        
        from google.genai.types import GenerateVideosConfig, Image, VideoGenerationReferenceImage
        import mimetypes
        
        client = get_gemini_client()
        
        try:
            # Prepare config with reference image if provided
            config = None
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
                
                # Read the image bytes
                with open(image_path, 'rb') as img_file:
                    image_bytes = img_file.read()
                
                # Determine MIME type
                mime_type, _ = mimetypes.guess_type(image_path)
                if not mime_type or not mime_type.startswith('image/'):
                    mime_type = "image/png"
                
                # Create config with reference images using the proper structure
                config = GenerateVideosConfig(
                    reference_images=[
                        VideoGenerationReferenceImage(
                            image=Image(
                                image_bytes=image_bytes,
                                mime_type=mime_type,
                            ),
                            reference_type="asset",
                        ),
                    ],
                )
            
            print(f"Submitting video generation request to Veo ({model})...")
            operation = client.models.generate_videos(
                model=model,
                prompt=self.prompt,
                config=config,
            )
            
            # Poll the operation status until the video is ready
            while not operation.done:
                print("Waiting for Veo video generation to complete...")
                time.sleep(10)
                operation = client.operations.get(operation)
            
            print("Video generation complete!")
            
            # Download the generated video
            generated_video = operation.response.generated_videos[0]
            output = save_veo_video_with_metadata(client, generated_video.video, self.name, self.product_name)
            
            return output
            
        except Exception as e:
            raise RuntimeError(f"Veo video generation failed: {str(e)}")


if __name__ == "__main__":
    tool = GenerateVideo(
        product_name="Test_Product",
        prompt=(
            "A person sitting on a bench with on-screen text saying 'Welcome to the future of AI'"
        ),
        seconds="4",
        size="1280x720",
        name="test_video",
        input_reference="D:/work/VRSEN/code/ad-factory-agent/mnt/Test_Product/generated_images/test_image.png",
    )
    try:
        result = tool.run()
        print(result)
    except Exception as exc:
        print(f"Video generation failed: {exc}")
