from agency_swarm.tools import BaseTool
from pydantic import Field, field_validator
import os
from pathlib import Path

# Define the base mnt directory
# Use container path in production, local path for development
if os.path.exists("/app"):
    MNT_DIR = Path("/app/mnt")
else:
    # Local development - use path relative to project root
    MNT_DIR = Path(__file__).parent.parent.parent / "mnt"

class ListDocuments(BaseTool):
    """
    Lists all markdown documents in a product's strategy_files folder.
    Use this tool to see what documents have been created for a specific product.
    """
    
    product_name: str = Field(
        ...,
        description="Name of the product to list documents for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract')."
    )
    
    @field_validator('product_name')
    @classmethod
    def validate_product_name(cls, v: str) -> str:
        """Validate and sanitize product name for use as folder name"""
        if not v or not v.strip():
            raise ValueError("Product name cannot be empty")
        
        # Sanitize product name for folder creation
        # Replace spaces with underscores, remove special characters
        sanitized = v.strip()
        sanitized = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in sanitized)
        sanitized = sanitized.replace(' ', '_')
        
        # Remove multiple consecutive underscores
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        if not sanitized:
            raise ValueError("Product name must contain at least one alphanumeric character")
        
        return sanitized
    
    def run(self) -> str:
        """
        Lists all .md files in the product's strategy_files folder.
        Returns a formatted list of documents with their file sizes.
        """
        # Step 1: Construct path to product's strategy_files folder
        product_dir = MNT_DIR / self.product_name / "strategy_files"
        
        # Step 2: Check if directory exists
        if not product_dir.exists():
            return f"No documents found. The folder for product '{self.product_name}' does not exist yet.\n\nFolder path: {product_dir}"
        
        if not product_dir.is_dir():
            return f"Error: Path exists but is not a directory: {product_dir}"
        
        # Step 3: List all .md files in the directory
        try:
            md_files = sorted(product_dir.glob("*.md"))
            
            if not md_files:
                return f"No markdown documents found in: {product_dir}\n\nThe folder exists but is empty."
            
            # Step 4: Format the output
            output_lines = [
                f"Documents for product: {self.product_name}",
                f"Location: {product_dir}",
                "",
                f"Found {len(md_files)} document(s):",
                ""
            ]
            
            for idx, file_path in enumerate(md_files, 1):
                # Get file size
                size_bytes = file_path.stat().st_size
                size_kb = size_bytes / 1024
                
                # Count lines
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                except:
                    line_count = 0
                
                output_lines.append(
                    f"{idx}. {file_path.name}\n"
                    f"   Size: {size_kb:.1f} KB ({size_bytes} bytes)\n"
                    f"   Lines: {line_count}"
                )
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"Error listing documents: {str(e)}"


if __name__ == "__main__":
    # Test case - create test documents first
    test_product_name = "Test_Product"
    test_dir = MNT_DIR / test_product_name / "strategy_files"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some test files
    test_files = [
        ("research_document.md", "# Research\n\nThis is research content.\n" * 50),
        ("avatar_sheet.md", "# Avatar\n\nAvatar details here.\n" * 20),
        ("offer_brief.md", "# Offer\n\nOffer details.\n" * 15),
    ]
    
    for filename, content in test_files:
        with open(test_dir / filename, 'w') as f:
            f.write(content)
    
    # Test the tool
    tool = ListDocuments(product_name=test_product_name)
    result = tool.run()
    print(result)
    
    # Test with non-existent product
    print("\n" + "=" * 60 + "\n")
    tool2 = ListDocuments(product_name="NonExistent_Product")
    result2 = tool2.run()
    print(result2)
    
    # Cleanup
    for filename, _ in test_files:
        os.remove(test_dir / filename)
    try:
        test_dir.rmdir()
        (MNT_DIR / test_product_name).rmdir()
    except OSError:
        pass

