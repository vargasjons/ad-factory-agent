"""Sora video generation tool for marketing content."""

from typing import Literal, Optional

from openai import OpenAI
from pydantic import Field, field_validator

from agency_swarm import BaseTool

from ad_factory_agent.tools.utils.video_utils import (
    SORA_MODEL,
    ensure_not_blank,
    get_openai_client,
    resolve_input_reference,
    validate_resolution,
    save_video_with_metadata,
)


class GenerateVideo(BaseTool):
    prompt: str = Field(
        ...,
        description=(
            "Detailed marketing description of the desired video. Include subjects, "
            "camera motion, lighting, and mood so Sora can synthesize the scene."
        ),
    )
    name: str = Field(
        ...,
        description="The name for the generated video file (without extension)",
    )
    seconds: Literal["4", "8", "12"] = Field(
        default="4",
        description="Clip length in seconds. Sora currently supports clips up to 12 seconds.",
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
    model: str = Field(
        default=SORA_MODEL,
        description="Video model identifier. Defaults to OpenAI's sora-2.",
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
        """Generate a marketing video using OpenAI's Sora 2 API."""

        client: OpenAI = get_openai_client()

        reference_file = None
        try:
            # Resolve and resize reference image to match video dimensions
            reference_file = resolve_input_reference(
                self.input_reference, 
                target_size=self.size if self.input_reference else None
            )

            request_payload = {
                "prompt": self.prompt,
                "model": self.model,
                "seconds": self.seconds,
            }
            if self.size:
                request_payload["size"] = self.size
            if reference_file is not None:
                request_payload["input_reference"] = reference_file

            print("Submitting video generation request to Sora...")
            video = client.videos.create_and_poll(**request_payload)
            print(f"Video generation status: {video.status}")

            # Save the generated video with all metadata
            output = save_video_with_metadata(client, video.id, self.name)

            return output

        finally:
            if reference_file is not None and hasattr(reference_file, "close"):
                try:
                    reference_file.close()
                except Exception:
                    pass


if __name__ == "__main__":
    tool = GenerateVideo(
        prompt=(
            "A person sitting on a bench with on-screen text saying 'Welcome to the future of AI'"
        ),
        seconds="4",
        size="1280x720",
        name="welcome_to_the_future_of_ai",
        # input_reference="laptop_last_frame",
    )
    try:
        result = tool.run()
        print(result)
    except Exception as exc:
        print(f"Video generation failed: {exc}")
