import os
import io
import base64
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from agents.tool import ToolOutputImage, ToolOutputText

# Constants
try:
    import sys
    from pathlib import Path
    # Add project root to path if needed
    project_root = str(Path(__file__).parent.parent.parent.parent)
    if project_root not in sys.path:
        sys.path.append(project_root)
    from onboarding_config import config
    MODEL_NAME = config.get("image_model", "gemini-2.5-flash-image-preview")
except ImportError:
    MODEL_NAME = "gemini-2.5-flash-image-preview"

# Base MNT directory
if os.path.exists("/app"):
    MNT_DIR = Path("/app/mnt")
else:
    # Local development - use path relative to project root
    MNT_DIR = Path(__file__).parent.parent.parent.parent / "mnt"

# Legacy path for backward compatibility (deprecated)
IMAGES_DIR = str(MNT_DIR / "generated_images")

OUTPUT_FORMAT = "png"


def get_images_dir(product_name: str) -> str:
    """
    Get the images directory for a specific product.
    
    Args:
        product_name: Name of the product (sanitized folder name)
        
    Returns:
        Path to product's generated_images directory
    """
    images_dir = MNT_DIR / product_name / "generated_images"
    images_dir.mkdir(parents=True, exist_ok=True)
    return str(images_dir)


def validate_num_variants(num_variants):
    """Validate num_variants parameter"""
    if num_variants < 1 or num_variants > 4:
        return "Error: num_variants must be between 1 and 4."
    return None


def get_api_key():
    """Get Google AI API key from environment"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None, "Error: Google AI API key not provided. Set GOOGLE_API_KEY environment variable."
    return api_key, None


def create_filename(file_name, variant_num, num_variants, output_format):
    """Create filename for image variant"""
    if num_variants == 1:
        image_name = file_name
    else:
        image_name = f"{file_name}_variant_{variant_num}"
    filename = f"{image_name}.{output_format}"
    return image_name, filename


def load_image_by_name(image_name, images_dir, extensions=None):
    """Load image by name, trying different extensions"""
    if extensions is None:
        extensions = ['.png', '.jpg', '.jpeg', '.webp']
    
    for ext in extensions:
        potential_path = os.path.join(images_dir, f"{image_name}{ext}")
        if os.path.exists(potential_path):
            try:
                image = Image.open(potential_path)
                return image, potential_path, None
            except Exception as e:
                return None, None, f"Error loading image {potential_path}: {str(e)}"
    
    return None, None, f"Error: Image file not found: {image_name} (tried {', '.join(extensions)})"


def extract_image_from_response(response):
    """Extract image from Gemini API response"""
    image = None
    text_output = ""
    
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            text_output += part.text
        elif part.inline_data is not None:
            image = Image.open(io.BytesIO(part.inline_data.data))
    
    return image, text_output


def extract_image_parts_from_response(response):
    """Extract image parts from Gemini API response (for combine_images)"""
    image_parts = [
        part.inline_data.data
        for part in response.candidates[0].content.parts
        if part.inline_data
    ]
    return image_parts


def process_variant_result(variant_num, image, file_name, num_variants, compress_func, images_dir=None):
    """Process a single variant result - save image and create result dict"""
    # Use provided images_dir or fall back to legacy IMAGES_DIR
    save_dir = images_dir if images_dir is not None else IMAGES_DIR
    
    # Create filename for this variant
    image_name, filename = create_filename(file_name, variant_num, num_variants, OUTPUT_FORMAT)
    filepath = os.path.join(save_dir, filename)
    
    # Save the image
    image.save(filepath, OUTPUT_FORMAT)
    
    # Convert image to compressed base64 for agent output
    compressed_b64 = compress_func(image)
    
    print(f"Variant {variant_num} saved to: {filepath}")
    
    return {
        "variant": variant_num,
        "file_path": filepath,
        "image_name": image_name,
        "base64": compressed_b64,
    }


async def run_parallel_variants(variant_func, num_variants):
    """Run multiple variants in parallel using asyncio and ThreadPoolExecutor"""
    results = []
    
    # Run synchronous variant_func in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    
    # Create tasks for all variants
    tasks = [
        loop.run_in_executor(None, variant_func, i + 1)
        for i in range(num_variants)
    ]
    
    # Wait for all tasks to complete
    completed_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out None results and exceptions
    for result in completed_results:
        if result is not None and not isinstance(result, Exception):
            results.append(result)
        elif isinstance(result, Exception):
            print(f"Variant generation error: {result}")
    
    return results


def create_result_summary(results, operation_name):
    """Create result summary text with file paths"""    
    result_text = f"Generated {len(results)} variant(s) successfully!\n"
    for result in results:
        result_text += f"  - {result['image_name']} → {result['file_path']}\n"
    return result_text


def create_image_urls(results, include_text_labels=False):
    """Create image URLs array for agent output with file paths"""    
    image_urls = []
    for result in results:
        if include_text_labels:
            image_urls.append(ToolOutputText(
                type="text", 
                text=f"{result['image_name']}:\nPath: {result['file_path']}\n"
            ))
        else:
            # For edit/combine tools, add file path before the image
            image_urls.append(ToolOutputText(
                type="text",
                text=f"Path: {result['file_path']}"
            ))
        
        # Add the base64 image preview
        image_urls.append(ToolOutputImage(
            type="image", 
            image_url=f"data:image/png;base64,{result['base64']}", 
            detail="auto"
        ))
    
    return image_urls


def image_to_base64(image, output_format='PNG'):
    """Convert image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format=output_format)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    return image_base64


def compress_image_for_base64(image, max_size=(800, 800), quality=65):
    """Compress image for base64 output while keeping original uncompressed and aspect ratio"""
    # Create a copy to avoid modifying the original
    compressed_image = image.copy()
    
    # Calculate new size while maintaining aspect ratio
    original_width, original_height = compressed_image.size
    max_width, max_height = max_size
    
    # Calculate scaling factor to fit within max_size while maintaining aspect ratio
    width_ratio = max_width / original_width
    height_ratio = max_height / original_height
    scale_factor = min(width_ratio, height_ratio, 1.0)  # Don't upscale
    
    # Only resize if the image is larger than max_size
    if scale_factor < 1.0:
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        compressed_image = compressed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Convert to RGB if necessary (for JPEG compression)
    if compressed_image.mode in ('RGBA', 'LA', 'P'):
        # Create a white background
        background = Image.new('RGB', compressed_image.size, (255, 255, 255))
        if compressed_image.mode == 'P':
            compressed_image = compressed_image.convert('RGBA')
        background.paste(compressed_image, mask=compressed_image.split()[-1] if compressed_image.mode == 'RGBA' else None)
        compressed_image = background
    
    # Save as JPEG with compression
    buffer = io.BytesIO()
    compressed_image.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)
    compressed_base64 = base64.b64encode(buffer.getvalue()).decode()
    return compressed_base64
