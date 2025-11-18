"""Tool for combining multiple images using Google's Gemini 2.5 Flash Image model."""

import io
import os
from typing import Literal

from google import genai
from PIL import Image
from pydantic import Field, field_validator

from agency_swarm import BaseTool

from ugc_agent.tools.utils.image_utils import (
    get_images_dir,
    MODEL_NAME,
    load_image_by_name,
    extract_image_parts_from_response,
    process_variant_result,
    run_parallel_variants,
    create_result_summary,
    create_image_urls,
    compress_image_for_base64,
)


class CombineImages(BaseTool):
    """Combine multiple images using Google's Gemini 2.5 Flash Image (Nano Banana) model.
    
    Images are saved to: mnt/{product_name}/generated_images/
    """

    product_name: str = Field(
        ...,
        description="Name of the product these images are for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract'). Used to organize files into product-specific folders.",
    )
    image_names: list[str] = Field(
        ...,
        description="List of image file names (without extension) to combine.",
    )
    text_instruction: str = Field(
        ...,
        description="Text instruction describing how to combine the images",
    )
    file_name: str = Field(
        ...,
        description="The name for the generated combined image file (without extension)",
    )
    num_variants: int = Field(
        default=1,
        description="Number of image variants to generate (1-4, default is 1)",
    )
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"] = Field(
        default="1:1",
        description="The aspect ratio of the generated image (default is 1:1)",
    )

    @field_validator("image_names")
    @classmethod
    def _validate_image_names(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("image_names must not be empty")
        if len(value) < 2:
            raise ValueError("At least 2 images are required for combining")
        for name in value:
            if not name.strip():
                raise ValueError("Image names must not be empty")
        return value

    @field_validator("text_instruction")
    @classmethod
    def _instruction_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text_instruction must not be empty")
        return value

    @field_validator("file_name")
    @classmethod
    def _filename_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("file_name must not be empty")
        return value

    @field_validator("num_variants")
    @classmethod
    def _validate_num_variants(cls, value: int) -> int:
        if value < 1 or value > 4:
            raise ValueError("num_variants must be between 1 and 4")
        return value

    async def run(self) -> list:
        """Combine images using the Gemini API."""

        # Step 1: Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable is required")

        print(f"Combining images with instruction: {self.text_instruction}")
        print(f"Generating {self.num_variants} variant(s)")

        # Step 2: Initialize the Google AI client
        client = genai.Client(api_key=api_key)

        # Step 3: Get product-specific images directory
        images_dir = get_images_dir(self.product_name)
        
        # Step 4: Load images using image names
        images = []
        for image_name in self.image_names:
            image, image_path, load_error = load_image_by_name(
                image_name, images_dir, [".png", ".jpg", ".jpeg"]
            )
            if load_error:
                raise FileNotFoundError(load_error)
            images.append(image)
            print(f"Loaded image: {image_path}")

        def combine_single_variant(variant_num: int):
            """Generate a single combined image variant"""
            try:
                print(f"Generating variant {variant_num}/{self.num_variants}")

                # Prepare contents for the API call
                contents = images + [self.text_instruction]

                # Generate combined image using Gemini 2.5 Flash Image
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=contents,
                    config=genai.types.GenerateContentConfig(
                        image_config=genai.types.ImageConfig(
                            aspect_ratio=self.aspect_ratio,
                        )
                    ),
                )

                # Extract the generated image
                image_parts = extract_image_parts_from_response(response)

                if not image_parts:
                    print(f"Warning: No image was generated for variant {variant_num}.")
                    return None

                # Create the combined image
                combined_image = Image.open(io.BytesIO(image_parts[0]))

                # Process variant result
                return process_variant_result(
                    variant_num,
                    combined_image,
                    self.file_name,
                    self.num_variants,
                    compress_image_for_base64,
                    images_dir,
                )
            except Exception as e:
                print(f"Error generating variant {variant_num}: {str(e)}")
                return None

        # Step 5: Run variants in parallel
        results = run_parallel_variants(combine_single_variant, self.num_variants)

        if not results:
            raise RuntimeError("No variants were successfully generated")

        # Step 6: Create and print result summary
        result_text = create_result_summary(results, "Generated")
        print(result_text)

        # Step 7: Return array of image URLs
        return create_image_urls(results, include_text_labels=False)

if __name__ == "__main__":
    import asyncio
    
    # Example usage with Google Gemini 2.5 Flash Image
    tool = CombineImages(
        product_name="Test_Product",
        image_names=["laptop_image_variant_2", "logo_image_variant_2"],
        text_instruction=(
            "Take the first image of a laptop on a table. Add the logo from the second image into the middle "
            "of the laptop. Remove the background of the logo and make it transparent. Ensure the laptop and "
            "features remain completely unchanged. The logo should look like it's naturally attached."
        ),
        file_name="laptop_with_logo",
        num_variants=2,
    )
    try:
        result = asyncio.run(tool.run())
        print(result)
    except Exception as exc:
        print(f"Image combining failed: {exc}")
