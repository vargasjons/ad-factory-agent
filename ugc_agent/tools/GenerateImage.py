"""Tool for generating images using Google's Gemini 2.5 Flash Image model."""

import os
from typing import Literal

from google import genai
from pydantic import Field, field_validator

from agency_swarm import BaseTool

from ugc_agent.tools.utils.image_utils import (
    get_images_dir,
    MODEL_NAME,
    extract_image_from_response,
    process_variant_result,
    run_parallel_variants,
    create_result_summary,
    create_image_urls,
    compress_image_for_base64,
)

from dotenv import load_dotenv

load_dotenv()


class GenerateImage(BaseTool):
    """Generate images using Google's Gemini 2.5 Flash Image (Nano Banana) model.
    
    Images are saved to: mnt/{product_name}/generated_images/
    """

    product_name: str = Field(
        ...,
        description="Name of the product this image is for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract'). Used to organize files into product-specific folders.",
    )
    prompt: str = Field(
        ...,
        description=(
            "The text prompt describing the image to generate. Start with 'Generate an image of' "
            "and describe the image in detail."
        ),
    )
    file_name: str = Field(
        ...,
        description="The name for the generated image file (without extension)",
    )
    num_variants: int = Field(
        default=1,
        description="Number of image variants to generate (1-4, default is 1)",
    )
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"] = Field(
        default="1:1",
        description="The aspect ratio of the generated image (default is 1:1)",
    )

    @field_validator("prompt")
    @classmethod
    def _prompt_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt must not be empty")
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

    def run(self) -> list:
        """Generate images using the Gemini API."""

        # Step 1: Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable is required")

        print(f"Generating image with prompt: {self.prompt}")
        print(f"Generating {self.num_variants} variant(s)")

        # Step 2: Initialize the Google AI client
        client = genai.Client(api_key=api_key)

        # Step 3: Get product-specific images directory
        images_dir = get_images_dir(self.product_name)

        def generate_single_variant(variant_num: int):
            """Generate a single image variant"""
            try:
                print(f"Generating variant {variant_num}/{self.num_variants}")

                # Generate image using Gemini 2.5 Flash Image
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[self.prompt],
                    config=genai.types.GenerateContentConfig(
                        image_config=genai.types.ImageConfig(
                            aspect_ratio=self.aspect_ratio,
                        )
                    ),
                )

                # Extract the generated image
                image, text_output = extract_image_from_response(response)

                if image is None:
                    print(
                        f"Warning: No image was generated for variant {variant_num}. "
                        f"Text output: {text_output}"
                    )
                    return None

                # Process variant result
                return process_variant_result(
                    variant_num,
                    image,
                    self.file_name,
                    self.num_variants,
                    compress_image_for_base64,
                    images_dir,
                )
            except Exception as e:
                print(f"Error generating variant {variant_num}: {str(e)}")
                return None

        # Step 4: Run variants in parallel
        results = run_parallel_variants(generate_single_variant, self.num_variants)

        if not results:
            raise RuntimeError("No variants were successfully generated")

        # Step 5: Create and print result summary
        result_text = create_result_summary(results, "Generated")
        print(result_text)

        # Step 6: Return array of image URLs
        return create_image_urls(results, include_text_labels=True)

if __name__ == "__main__":
    # Example usage with Google Gemini 2.5 Flash Image
    tool = GenerateImage(
        product_name="Test_Product",
        prompt=(
            "Generate an image of a clean, modern black laptop computer that is placed closed on a white marble "
            "surface with soft natural lighting, professional product photography style, shallow depth of field, "
            "premium aesthetic, commercial advertisement quality. No logo images. No text"
        ),
        file_name="test_image",
        aspect_ratio="16:9",
    )
    try:
        result = tool.run()
        print(result)
    except Exception as exc:
        print(f"Image generation failed: {exc}")
