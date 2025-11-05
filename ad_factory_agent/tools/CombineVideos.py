"""Tool for combining multiple videos into a single video."""

import os
from typing import Literal

from pydantic import Field, field_validator

from agency_swarm import BaseTool

from ad_factory_agent.tools.utils.video_utils import VIDEO_DIR


class CombineVideos(BaseTool):
    """Combine multiple videos into a single video using sequential concatenation."""

    video_names: list[str] = Field(
        ...,
        description="List of video file names (without extension) to combine in order.",
    )
    name: str = Field(
        ...,
        description="The name for the combined video file (without extension)",
    )
    transition: Literal["cut", "fade"] = Field(
        default="cut",
        description="Transition type between videos: 'cut' for instant or 'fade' for smooth transition",
    )

    @field_validator("video_names")
    @classmethod
    def _validate_video_names(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("video_names must not be empty")
        if len(value) < 2:
            raise ValueError("At least 2 videos are required for combining")
        for name in value:
            if not name.strip():
                raise ValueError("Video names must not be empty")
        return value

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name must not be empty")
        return value

    def run(self) -> list:
        """Combine videos using moviepy."""

        # Step 1: Import moviepy (lazy import)
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips
        except ImportError:
            raise RuntimeError(
                "moviepy is required for video combining. Install it with: pip install moviepy"
            )

        print(f"Combining {len(self.video_names)} videos: {', '.join(self.video_names)}")
        print(f"Transition type: {self.transition}")

        # Step 2: Load all video clips
        video_clips = []
        video_paths = []
        
        for video_name in self.video_names:
            # Try to find the video with .mp4 extension
            video_path = os.path.join(VIDEO_DIR, f"{video_name}.mp4")
            
            if not os.path.exists(video_path):
                raise FileNotFoundError(
                    f"Video file not found: {video_path}. "
                    f"Make sure the video exists in the {VIDEO_DIR} directory."
                )
            
            print(f"Loading video: {video_path}")
            video_clip = VideoFileClip(video_path)
            video_clips.append(video_clip)
            video_paths.append(video_path)

        # Step 3: Apply transitions if needed
        if self.transition == "fade":
            print("Applying fade transitions...")
            # Apply fade out to all clips except the last one
            for i in range(len(video_clips) - 1):
                video_clips[i] = video_clips[i].crossfadeout(0.5)
            
            # Apply fade in to all clips except the first one
            for i in range(1, len(video_clips)):
                video_clips[i] = video_clips[i].crossfadein(0.5)

        # Step 4: Concatenate videos
        print("Concatenating videos...")
        try:
            final_clip = concatenate_videoclips(
                video_clips,
                method="compose" if self.transition == "fade" else "chain"
            )
            
            # Step 5: Save the combined video
            os.makedirs(VIDEO_DIR, exist_ok=True)
            output_path = os.path.join(VIDEO_DIR, f"{self.name}.mp4")
            
            print(f"Writing combined video to: {output_path}")
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                logger=None,  # Suppress moviepy progress bar for cleaner output
            )
            
        finally:
            # Step 6: Clean up - close all clips to free resources
            print("Cleaning up resources...")
            for clip in video_clips:
                clip.close()
            if 'final_clip' in locals():
                final_clip.close()

        # Step 7: Create output summary
        from agency_swarm import ToolOutputText
        
        output = []
        
        # Add summary of combined videos
        summary = f"Successfully combined {len(self.video_names)} videos:\n"
        for i, name in enumerate(self.video_names, 1):
            summary += f"  {i}. {name}.mp4\n"
        summary += f"\nCombined video saved to `{self.name}.mp4`"
        
        output.append(ToolOutputText(type="text", text=summary))
        
        print(f"\n{summary}")
        
        return output


if __name__ == "__main__":
    # Example usage
    tool = CombineVideos(
        video_names=["laptop", "laptop_pt2"],
        name="laptop_combined",
        transition="cut",
    )
    try:
        result = tool.run()
        print(result)
    except Exception as exc:
        print(f"Video combining failed: {exc}")

