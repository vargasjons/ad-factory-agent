"""Tool for combining multiple videos into a single video using ffmpeg."""

import os
import subprocess
import tempfile

from pydantic import Field, field_validator

from agency_swarm import BaseTool, ToolOutputText

from ugc_agent.tools.utils.video_utils import VIDEO_DIR


class CombineVideos(BaseTool):
    """Combine multiple videos into a single video using instant cut transitions (ffmpeg)."""

    video_names: list[str] = Field(
        ...,
        description="List of video file names (without extension) to combine in order.",
    )
    name: str = Field(
        ...,
        description="The name for the combined video file (without extension)",
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
        """Combine videos using ffmpeg concat demuxer."""

        print(f"Combining {len(self.video_names)} videos: {', '.join(self.video_names)}")

        # Step 1: Verify all video files exist and collect paths
        video_paths = []
        
        for video_name in self.video_names:
            video_path = os.path.join(VIDEO_DIR, f"{video_name}.mp4")
            
            if not os.path.exists(video_path):
                raise FileNotFoundError(
                    f"Video file not found: {video_path}. "
                    f"Make sure the video exists in the {VIDEO_DIR} directory."
                )
            
            print(f"Found video: {video_path}")
            video_paths.append(video_path)

        # Step 2: Create output directory
        os.makedirs(VIDEO_DIR, exist_ok=True)
        output_path = os.path.join(VIDEO_DIR, f"{self.name}.mp4")
        
        # Step 3: Use ffmpeg concat demuxer for instant cuts
        print("Using ffmpeg concat demuxer for cut transitions...")
        
        # Create a temporary file list for ffmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            for path in video_paths:
                # Convert to absolute path and use forward slashes
                abs_path = os.path.abspath(path).replace('\\', '/')
                # Escape single quotes in path
                escaped_path = abs_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
            concat_file = f.name
        
        try:
            # Use ffmpeg to concatenate
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',  # Copy streams without re-encoding (fastest)
                '-y',  # Overwrite output file if exists
                output_path
            ]
            
            print("Running ffmpeg concatenation...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"FFmpeg concatenation failed: {result.stderr}")
                
        finally:
            # Clean up temp file
            try:
                os.unlink(concat_file)
            except Exception:
                pass
        
        output = []
        
        # Add summary of combined videos with file path
        summary = f"✅ Successfully combined {len(self.video_names)} videos:\n"
        for i, name in enumerate(self.video_names, 1):
            summary += f"  {i}. {name}.mp4\n"
        summary += f"\n📹 Output: {self.name}.mp4\n"
        summary += f"Path: {output_path}"
        
        output.append(ToolOutputText(type="text", text=summary))
        
        print(f"\n{summary}")
        
        return output


if __name__ == "__main__":
    # Example usage
    tool = CombineVideos(
        video_names=["herbaluxe_01_hook_v2","herbaluxe_02_formula","herbaluxe_03_result_consistency_fix","herbaluxe_04_cta"],
        name="x_combine_test",
    )
    result = tool.run()
    print(result)

