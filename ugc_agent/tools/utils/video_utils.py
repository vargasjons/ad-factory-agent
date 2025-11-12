"""Shared utilities for Sora video tools."""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import cv2
import httpx
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

from agency_swarm import ToolOutputText, ToolOutputImage


load_dotenv()

SORA_MODEL = "sora-2"

# Use container path in production, local path for development
if os.path.exists("/app"):
    VIDEO_DIR = "/app/mnt/generated_videos"
else:
    # Local development - use path relative to project root
    VIDEO_DIR = str(Path(__file__).parent.parent.parent.parent / "mnt" / "generated_videos")

def get_openai_client() -> OpenAI:
    """Instantiate an OpenAI client using the API key from the environment."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is required for video operations"
        )
    return OpenAI(api_key=api_key)


def parse_video_size(size: str) -> tuple[int, int]:
    """
    Parse video size string into width and height tuple.
    
    Args:
        size: Size string in WIDTHxHEIGHT format (e.g. '1280x720')
    
    Returns:
        Tuple of (width, height)
    """
    parts = size.lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"Invalid size format: {size}")
    return int(parts[0]), int(parts[1])


def resize_image_to_dimensions(image: Image.Image, width: int, height: int) -> Image.Image:
    """
    Resize an image to match specific dimensions while maintaining aspect ratio.
    
    Args:
        image: PIL Image to resize
        width: Target width
        height: Target height
    
    Returns:
        Resized PIL Image
    """
    # Calculate aspect ratios
    target_ratio = width / height
    image_ratio = image.width / image.height
    
    if abs(target_ratio - image_ratio) < 0.01:
        # Aspect ratios are close enough, just resize directly
        return image.resize((width, height), Image.Resampling.LANCZOS)
    
    # Aspect ratios differ, crop to match target ratio first
    if image_ratio > target_ratio:
        # Image is wider than target, crop width
        new_width = int(image.height * target_ratio)
        left = (image.width - new_width) // 2
        image = image.crop((left, 0, left + new_width, image.height))
    else:
        # Image is taller than target, crop height
        new_height = int(image.width / target_ratio)
        top = (image.height - new_height) // 2
        image = image.crop((0, top, image.width, top + new_height))
    
    # Now resize to exact dimensions
    return image.resize((width, height), Image.Resampling.LANCZOS)


def resolve_input_reference(reference: Optional[str], target_size: Optional[str] = None) -> Optional[io.BufferedReader]:
    """
    Turn an image name, local path, or HTTPS URL into a binary file handle for the API.
    Optionally resizes the image to match target video dimensions.
    
    Args:
        reference: Image name (without extension), full path, or URL to the reference image
        target_size: Optional target size in WIDTHxHEIGHT format (e.g. '1280x720')
    
    Returns:
        Binary file handle ready for API upload
    """
    if reference is None:
        return None

    # Step 1: Load the image from URL, local path, or image name
    parsed = urlparse(reference)
    
    if parsed.scheme in ("http", "https"):
        # Handle URL
        print("Downloading reference image from URL...")
        with httpx.Client(timeout=30.0) as client:
            response = client.get(reference)
            response.raise_for_status()
            image_data = io.BytesIO(response.content)
            filename = Path(parsed.path).name or "reference.png"
    else:
        # Try as full path first
        path = Path(reference).expanduser().resolve()
        
        if path.exists():
            # Handle full path
            print(f"Loading reference image from {path}...")
            with open(path, "rb") as f:
                image_data = io.BytesIO(f.read())
            filename = path.name
        else:
            # Try as image name without extension in multiple directories
            from ugc_agent.tools.utils.image_utils import load_image_by_name, IMAGES_DIR
            
            pil_image = None
            image_path = None
            
            # Try in generated_images directory first
            print(f"Looking for image '{reference}' in {IMAGES_DIR}...")
            pil_image, image_path, load_error_images = load_image_by_name(
                reference, IMAGES_DIR, [".png", ".jpg", ".jpeg", ".webp"]
            )
            
            # If not found, try in generated_videos directory (for thumbnails/spritesheets)
            if load_error_images:
                print(f"Not found in {IMAGES_DIR}, trying {VIDEO_DIR}...")
                pil_image, image_path, load_error_videos = load_image_by_name(
                    reference, VIDEO_DIR, [".png", ".jpg", ".jpeg", ".webp"]
                )
            
            if pil_image is None:
                raise FileNotFoundError("Reference image not found.")
            
            print(f"Loaded image: {image_path}")
            
            # Convert PIL Image to BytesIO
            image_data = io.BytesIO()
            pil_image.save(image_data, format=pil_image.format or "PNG")
            image_data.seek(0)
            filename = Path(image_path).name
    
    # Step 2: Resize the image if target_size is provided
    if target_size:
        print(f"Resizing reference image to match video dimensions: {target_size}")
        image_data.seek(0)
        image = Image.open(image_data)
        
        # Get target dimensions
        width, height = parse_video_size(target_size)
        
        # Resize the image
        resized_image = resize_image_to_dimensions(image, width, height)
        
        # Save resized image to buffer
        buffer = io.BytesIO()
        # Preserve format or use PNG as default
        image_format = image.format or "PNG"
        resized_image.save(buffer, format=image_format)
        buffer.seek(0)
        buffer.name = filename
        
        print(f"Reference image resized from {image.width}x{image.height} to {width}x{height}")
        return buffer  # type: ignore[return-value]
    
    # Step 3: Return original image if no resizing needed
    image_data.seek(0)
    image_data.name = filename
    return image_data  # type: ignore[return-value]


def validate_resolution(value: Optional[str]) -> Optional[str]:
    """Ensure a resolution string is in WIDTHxHEIGHT format."""

    if value is None:
        return None
    parts = value.lower().split("x")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError("size must be formatted as WIDTHxHEIGHT (e.g. 1280x720)")
    return value


def ensure_not_blank(value: str, field_name: str) -> str:
    """Raise if a text field is empty or whitespace only."""

    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


def download_video_variant(client: OpenAI, video_id: str, variant: str, output_path: str) -> None:
    """
    Download a specific variant of a video from Sora API.
    
    Args:
        client: OpenAI client instance
        video_id: The video ID from Sora API
        variant: Type of content to download (spritesheet, thumbnail, or video)
        output_path: Full path where the file should be saved
    """
    print(f"Downloading {variant} for video {video_id}...")
    content = client.videos.download_content(video_id, variant=variant)
    content.write_to_file(output_path)


def create_image_output(image_path: str, label: str) -> list:
    """
    Create tool output objects for an image file.
    
    Args:
        image_path: Path to the image file
        label: Label to display for the image (filename)
    
    Returns:
        List containing ToolOutputText and ToolOutputImage objects
    """
    from ugc_agent.tools.utils.image_utils import compress_image_for_base64
    
    image = Image.open(image_path)
    compressed_b64 = compress_image_for_base64(image)
    
    return [
        ToolOutputText(type="text", text=f"{label}\nPath: {image_path}"),
        ToolOutputImage(type="image", image_url=f"data:image/png;base64,{compressed_b64}", detail="auto")
    ]


def extract_last_frame(video_path: str, output_path: str) -> Optional[Image.Image]:
    """
    Extract the last frame from a video file.
    
    Args:
        video_path: Path to the video file
        output_path: Path where the last frame image should be saved
    
    Returns:
        PIL Image object of the last frame, or None if extraction failed
    """
    print("Extracting last frame from video...")
    cap = cv2.VideoCapture(video_path)
    
    # Get total frame count and set to last frame
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    ret, frame = cap.read()
    
    cap.release()
    
    if not ret:
        return None
    
    # Convert BGR to RGB (OpenCV uses BGR)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    last_frame_image = Image.fromarray(frame_rgb)
    
    # Save last frame
    last_frame_image.save(output_path)
    
    return last_frame_image


def save_video_with_metadata(client: OpenAI, video_id: str, name: str) -> list:
    """
    Download and save video with all metadata (spritesheet, thumbnail, last frame).
    
    Args:
        client: OpenAI client instance
        video_id: The video ID from Sora API
        name: Base name for saved files (without extension)
    
    Returns:
        List of ToolOutput objects showing the saved files
    """
    output = []
    os.makedirs(VIDEO_DIR, exist_ok=True)
    
    # Step 1: Download and save spritesheet
    spritesheet_path = os.path.join(VIDEO_DIR, f"{name}_spritesheet.jpg")
    download_video_variant(client, video_id, "spritesheet", spritesheet_path)
    output.extend(create_image_output(spritesheet_path, f"{name}_spritesheet.jpg"))
    
    # Step 2: Download and save thumbnail
    thumbnail_path = os.path.join(VIDEO_DIR, f"{name}_thumbnail.jpg")
    download_video_variant(client, video_id, "thumbnail", thumbnail_path)
    output.extend(create_image_output(thumbnail_path, f"{name}_thumbnail.jpg"))
    
    # Step 3: Download and save the actual video
    video_path = os.path.join(VIDEO_DIR, f"{name}.mp4")
    download_video_variant(client, video_id, "video", video_path)
    
    # Step 4: Extract and save the last frame
    last_frame_path = os.path.join(VIDEO_DIR, f"{name}_last_frame.jpg")
    last_frame_image = extract_last_frame(video_path, last_frame_path)
    
    if last_frame_image:
        output.extend(create_image_output(last_frame_path, f"{name}_last_frame.jpg"))
    
    # Step 5: Add final summary message with full path
    output.append(ToolOutputText(type="text", text=f"Video saved to `{name}.mp4`\nPath: {video_path}\nVideo ID: {video_id}"))
    
    return output


