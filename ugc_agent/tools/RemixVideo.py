"""Tool for remixing existing Sora videos."""

from openai import OpenAI
from pydantic import Field, field_validator, model_validator

from agency_swarm import BaseTool

from ugc_agent.tools.utils.video_utils import (
    ensure_not_blank,
    get_openai_client,
    save_video_with_metadata,
)

# Import config to check video generation model
try:
    from onboarding_config import config
except ImportError:
    config = {"video_generation_model": "sora-2"}  # Default to Sora if config not found


class RemixVideo(BaseTool):
    """
    Adjust an existing video by providing a new creative direction.
    
    Videos are saved to: mnt/{product_name}/generated_videos/
    """

    product_name: str = Field(
        ...,
        description="Name of the product this video is for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract'). Used to organize files into product-specific folders.",
    )
    video_id: str = Field(
        ...,
        description="Identifier of the previously generated video job to remix.",
    )
    prompt: str = Field(
        ...,
        description=(
            "Revised scene description that guides the remix. Describe stylistic "
            "changes, pacing, or new narrative elements."
        ),
    )
    name: str = Field(
        ...,
        description="The name for the remixed video file (without extension)",
    )

    @field_validator("video_id")
    @classmethod
    def _id_not_blank(cls, value: str) -> str:
        return ensure_not_blank(value, "video_id")

    @field_validator("prompt")
    @classmethod
    def _prompt_not_blank(cls, value: str) -> str:
        return ensure_not_blank(value, "prompt")

    @model_validator(mode='after')
    def _check_model_is_sora(self):
        """Validate that the video generation model is Sora (remix not supported by Veo)."""
        video_model = config.get("video_generation_model", "sora-2")
        
        # Check if model is Veo (starts with "veo-")
        if video_model.startswith("veo-"):
            raise ValueError(
                "Remix Video is not supported with current video generation model.\n\n"
                "To modify a Veo video:\n"
                "1. Regenerate the video with a modified prompt using GenerateVideo\n"
                "2. Use the same reference image or 1st starting frame if needed for consistency\n\n"
            )
        
        return self

    async def run(self) -> list:
        """Send a remix request to the Sora API, poll until completion, and save the video."""

        client: OpenAI = get_openai_client()

        print("Submitting video remix request to Sora...")
        video = client.videos.remix(
            video_id=self.video_id,
            prompt=self.prompt,
        )
        
        print(f"Remix job created: {video.id}, status: {video.status}")
        
        # Poll until the video is completed or failed
        video = client.videos.poll(video.id)
        
        print(f"Video remix status: {video.status}")
        
        # Save the remixed video with all metadata
        output = save_video_with_metadata(client, video.id, self.name, self.product_name)
        
        return output


if __name__ == "__main__":
    import asyncio
    
    tool = RemixVideo(
        product_name="Test_Product",
        video_id="video_690ae26779a88191afbc43b9bc4151a007197f9b393bc6f9",
        prompt="Change what the podcaster is talking about. They should instead say: 'It can generate super-realistic videos in only ten seconds with a single prompt.'",
        name="podcaster_1_remix",
    )
    try:
        print(asyncio.run(tool.run()))
    except Exception as exc:
        print(f"Video remix failed: {exc}")


