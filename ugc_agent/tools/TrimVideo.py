"""Tool for trimming videos from start and/or end."""

import os
from typing import Optional
import asyncio

from pydantic import Field, field_validator, model_validator
from agency_swarm import BaseTool

from ugc_agent.tools.utils.video_utils import (
    get_videos_dir,
    ensure_not_blank,
    generate_spritesheet,
    extract_last_frame,
    create_image_output,
)
from agency_swarm import ToolOutputText


class TrimVideo(BaseTool):
    """
    Trim a video by removing seconds from the start and/or end.
    
    Useful for removing unwanted intro/outro segments or adjusting video length.
    
    Videos are saved to: mnt/{product_name}/generated_videos/
    """
    
    product_name: str = Field(
        ...,
        description="Name of the product this video is for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract'). Used to organize files into product-specific folders.",
    )
    input_video: str = Field(
        ...,
        description=(
            "The video to trim. Can be: "
            "1) Video name without extension (searches generated_videos folder), "
            "2) Full local path to video file."
        ),
    )
    output_name: str = Field(
        ...,
        description="The name for the trimmed video file (without extension)",
    )
    trim_start: Optional[float] = Field(
        default=None,
        description="Seconds to trim from the start of the video (optional, defaults to 0.0 if not provided)",
    )
    trim_end: Optional[float] = Field(
        default=None,
        description="Seconds to trim from the end of the video (optional, defaults to 0.0 if not provided)",
    )
    
    @field_validator("input_video")
    @classmethod
    def _input_not_blank(cls, value: str) -> str:
        return ensure_not_blank(value, "input_video")
    
    @field_validator("output_name")
    @classmethod
    def _output_not_blank(cls, value: str) -> str:
        return ensure_not_blank(value, "output_name")
    
    @model_validator(mode='after')
    def _validate_and_set_defaults(self):
        """Set defaults and validate that at least one trim parameter is provided (> 0)"""
        # Set defaults
        if self.trim_start is None:
            self.trim_start = 0.0
        if self.trim_end is None:
            self.trim_end = 0.0
        
        # Validate non-negative
        if self.trim_start < 0:
            raise ValueError("trim_start must be non-negative")
        if self.trim_end < 0:
            raise ValueError("trim_end must be non-negative")
        
        # Ensure at least one is provided
        if self.trim_start == 0.0 and self.trim_end == 0.0:
            raise ValueError(
                "At least one of trim_start or trim_end must be greater than 0. "
                "Provide at least one trim value."
            )
        
        return self
    
    async def run(self) -> list:
        """Trim the video and save with metadata."""
        
        # Step 1: Resolve input video path
        input_path = self._resolve_video_path()
        print(f"Input video: {input_path}")
        
        # Step 2: Get output directory and path
        videos_dir = get_videos_dir(self.product_name)
        output_path = os.path.join(videos_dir, f"{self.output_name}.mp4")
        
        # Step 3: Trim the video
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._trim_video_blocking,
            input_path,
            output_path
        )
        
        # Step 4: Generate metadata (spritesheet, thumbnail, last frame)
        output = []
        
        # Generate spritesheet
        spritesheet_path = os.path.join(videos_dir, f"{self.output_name}_spritesheet.jpg")
        spritesheet = await loop.run_in_executor(
            None,
            generate_spritesheet,
            output_path,
            spritesheet_path
        )
        if spritesheet:
            output.extend(create_image_output(spritesheet_path, f"{self.output_name}_spritesheet.jpg"))
        
        # Extract and save thumbnail (first frame)
        thumbnail_path = os.path.join(videos_dir, f"{self.output_name}_thumbnail.jpg")
        thumbnail = await loop.run_in_executor(
            None,
            self._extract_first_frame,
            output_path,
            thumbnail_path
        )
        if thumbnail:
            output.extend(create_image_output(thumbnail_path, f"{self.output_name}_thumbnail.jpg"))
        
        # Extract and save last frame
        last_frame_path = os.path.join(videos_dir, f"{self.output_name}_last_frame.jpg")
        last_frame = await loop.run_in_executor(
            None,
            extract_last_frame,
            output_path,
            last_frame_path
        )
        if last_frame:
            output.extend(create_image_output(last_frame_path, f"{self.output_name}_last_frame.jpg"))
        
        # Step 5: Add final summary message
        output.append(ToolOutputText(
            type="text",
            text=f"Video trimmed successfully!\nSaved to: `{self.output_name}.mp4`\nPath: {output_path}\nTrimmed: {self.trim_start}s from start, {self.trim_end}s from end"
        ))
        
        return output
    
    def _resolve_video_path(self) -> str:
        """Resolve input video to full path."""
        from pathlib import Path
        
        # Try as full path first
        path = Path(self.input_video).expanduser().resolve()
        
        if path.exists():
            return str(path)
        
        # Try as video name without extension in generated_videos
        videos_dir = get_videos_dir(self.product_name)
        
        for ext in [".mp4", ".mov", ".avi", ".webm"]:
            potential_path = os.path.join(videos_dir, f"{self.input_video}{ext}")
            if os.path.exists(potential_path):
                return potential_path
        
        raise FileNotFoundError(
            f"Video '{self.input_video}' not found in {videos_dir}. "
            f"Tried extensions: .mp4, .mov, .avi, .webm"
        )
    
    def _trim_video_blocking(self, input_path: str, output_path: str) -> None:
        """Trim video using ffmpeg (blocking operation)."""
        import subprocess
        import cv2
        
        print(f"Trimming video: {self.trim_start}s from start, {self.trim_end}s from end")
        
        # Step 1: Get video duration for validation
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_duration = total_frames / fps
        cap.release()
        
        # Step 2: Calculate output duration
        output_duration = original_duration - self.trim_start - self.trim_end
        
        # Validate trim parameters
        if output_duration <= 0:
            raise ValueError(
                f"Invalid trim parameters: output duration would be {output_duration:.2f}s. "
                f"Video duration is {original_duration:.2f}s. "
                f"Reduce trim_start ({self.trim_start}s) and/or trim_end ({self.trim_end}s)."
            )
        
        print(f"Original duration: {original_duration:.2f}s")
        print(f"Output duration: {output_duration:.2f}s")
        
        # Step 3: Build ffmpeg command for trimming
        # Using -ss (start time) and -t (duration) for precise trimming
        # -c copy would be fastest but may have keyframe issues, so we re-encode with H.264
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-i", input_path,  # Input file
            "-ss", str(self.trim_start),  # Start time
            "-t", str(output_duration),  # Duration
            "-c:v", "libx264",  # Video codec: H.264
            "-preset", "medium",  # Encoding preset (balance speed/quality)
            "-crf", "23",  # Constant Rate Factor (quality: 0-51, lower is better)
            "-c:a", "aac",  # Audio codec
            "-b:a", "128k",  # Audio bitrate
            "-movflags", "+faststart",  # Enable fast start for web playback
            "-pix_fmt", "yuv420p",  # Pixel format for compatibility
            output_path
        ]
        
        print("Running ffmpeg command...")
        print(f"Start: {self.trim_start}s, Duration: {output_duration:.2f}s")
        
        # Step 4: Run ffmpeg
        try:
            subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            print(f"Trimmed video saved: {output_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"ffmpeg failed to trim video. Error: {e.stderr}"
            )
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg and ensure it's in your PATH. "
                "Download from: https://ffmpeg.org/download.html"
            )
    
    def _extract_first_frame(self, video_path: str, output_path: str) -> Optional[object]:
        """Extract the first frame from video as thumbnail."""
        import cv2
        from PIL import Image
        
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        thumbnail_image = Image.fromarray(frame_rgb)
        thumbnail_image.save(output_path)
        
        return thumbnail_image


if __name__ == "__main__":
    import asyncio
    
    # Example: Trim only from start (trim_end defaults to 0.0)
    tool = TrimVideo(
        product_name="Test_Product",
        input_video="test_video",  # Will look for test_video.mp4 in generated_videos
        output_name="test_video_trimmed",
        # trim_start=1.0,  # Trim 1 second from start
        trim_end=1.0
    )
    
    try:
        result = asyncio.run(tool.run())
        print("\nTrim complete!")
        print(result)
    except Exception as exc:
        print(f"Video trim failed: {exc}")

