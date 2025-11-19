"""Tool for listing available brand assets from the brand_assets folder."""

import os
from pathlib import Path
from pydantic import Field
from agency_swarm import BaseTool


class ListBrandAssets(BaseTool):
    """
    Lists all brand assets available in the brand_assets folder.
    Returns file paths and basic information about each asset.
    
    Brand assets include logos, images, fonts, and other brand materials
    uploaded during onboarding or added manually to ./mnt/brand_assets/
    """
    
    include_hidden: bool = Field(
        default=False,
        description="Whether to include hidden files (files starting with .)"
    )

    def run(self):
        """
        Lists all brand assets from the ./mnt/brand_assets folder.
        
        Returns:
            A formatted string with paths to all brand assets, organized by file type.
        """
        # Get the root directory (3 levels up from this file: tools -> ugc_agent -> root)
        root_dir = Path(__file__).resolve().parent.parent.parent
        brand_assets_dir = root_dir / "mnt" / "brand_assets"
        
        # Check if the directory exists
        if not brand_assets_dir.exists():
            return (
                f"Brand assets directory does not exist: {brand_assets_dir}\n\n"
                "To add brand assets:\n"
                "1. Run the onboarding tool and upload files, or\n"
                "2. Manually create the folder and add files to: ./mnt/brand_assets/"
            )
        
        # Get all files in the directory (recursively)
        all_files = []
        for root, dirs, files in os.walk(brand_assets_dir):
            for file in files:
                # Skip hidden files unless requested
                if not self.include_hidden and file.startswith('.'):
                    continue
                
                file_path = Path(root) / file
                relative_path = file_path.relative_to(root_dir)
                file_size = file_path.stat().st_size
                
                all_files.append({
                    'path': str(relative_path),
                    'absolute_path': str(file_path),
                    'name': file,
                    'extension': file_path.suffix.lower(),
                    'size_bytes': file_size,
                    'size_readable': self._format_size(file_size),
                })
        
        if not all_files:
            return (
                f"No brand assets found in: {brand_assets_dir}\n\n"
                "To add brand assets:\n"
                "1. Run the onboarding tool and upload files, or\n"
                "2. Manually add files to: ./mnt/brand_assets/"
            )
        
        # Organize by file type
        images = []
        fonts = []
        videos = []
        other = []
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}
        font_extensions = {'.ttf', '.otf', '.woff', '.woff2'}
        video_extensions = {'.mp4', '.mov', '.avi', '.webm', '.mkv'}
        
        for file in all_files:
            ext = file['extension']
            if ext in image_extensions:
                images.append(file)
            elif ext in font_extensions:
                fonts.append(file)
            elif ext in video_extensions:
                videos.append(file)
            else:
                other.append(file)
        
        # Build the output
        output = [f"Found {len(all_files)} brand asset(s) in {brand_assets_dir}\n"]
        
        if images:
            output.append(f"\n📷 IMAGES ({len(images)}):")
            for img in images:
                output.append(f"  • {img['path']} ({img['size_readable']})")
        
        if fonts:
            output.append(f"\n🔤 FONTS ({len(fonts)}):")
            for font in fonts:
                output.append(f"  • {font['path']} ({font['size_readable']})")
        
        if videos:
            output.append(f"\n🎬 VIDEOS ({len(videos)}):")
            for video in videos:
                output.append(f"  • {video['path']} ({video['size_readable']})")
        
        if other:
            output.append(f"\n📄 OTHER FILES ({len(other)}):")
            for file in other:
                output.append(f"  • {file['path']} ({file['size_readable']})")
        
        output.append("\n\nUsage:")
        output.append("  Use these paths to reference brand assets in your prompts.")
        output.append("  For example, you can use images as reference images in GenerateImage or GenerateVideo tools.")
        
        return "\n".join(output)
    
    def _format_size(self, bytes_size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"


if __name__ == "__main__":
    # Test the tool
    tool = ListBrandAssets()
    print(tool.run())

