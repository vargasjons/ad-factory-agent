"""Tool for remixing existing Sora videos."""

from openai import OpenAI
from pydantic import Field, field_validator

from agency_swarm import BaseTool

from ad_factory_agent.tools.utils.video_utils import (
    ensure_not_blank,
    get_openai_client,
    save_video_with_metadata,
)


class RemixVideo(BaseTool):
    """Adjust an existing video by providing a new creative direction."""

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

    def run(self) -> list:
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
        output = save_video_with_metadata(client, video.id, self.name)
        
        return output


if __name__ == "__main__":
    tool = RemixVideo(
        video_id="video_690ae26779a88191afbc43b9bc4151a007197f9b393bc6f9",
        prompt="Change what the podcaster is talking about. They should instead say: 'It can generate super-realistic videos in only ten seconds with a single prompt.'",
        name="podcaster_1_remix",
    )
    try:
        print(tool.run())
    except Exception as exc:
        print(f"Video remix failed: {exc}")


