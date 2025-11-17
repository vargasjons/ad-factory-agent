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

class CreateDocument(BaseTool):
    """
    Creates and saves a markdown document to the strategy_agent/files folder, organized by product.
    Use this tool to save the foundational documents: Research Document, Avatar Sheet, 
    Offer Brief, and Necessary Beliefs documents.
    
    Documents are organized in product-specific sub-folders for better organization.
    """
    
    product_name: str = Field(        ...,
        description="Name of the product this document is for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract'). Used to organize files into product-specific sub-folders."
    )
    
    filename: str = Field(
        ..., 
        description="Name of the file to create (e.g., 'brand_research_document.md'). Must end with .md extension."
    )
    
    content: str = Field(
        ..., 
        description="The complete content of the document in markdown format. Should be comprehensive and well-structured."
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
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate that filename ends with .md"""
        if not v.endswith('.md'):
            raise ValueError("Filename must end with .md extension")
        
        # Remove any path separators for security
        v = os.path.basename(v)
        
        if not v or v == '.md':
            raise ValueError("Filename cannot be empty")
            
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is not empty"""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v

    def run(self) -> str:
        """
        Creates the document and saves it to mnt/{product_name}/strategy_files/ folder.
        Returns a success message with the file path.
        """
        # Step 1: Create product-specific directory structure
        product_dir = MNT_DIR / self.product_name / "strategy_files"
        product_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 2: Create full file path within product folder
        file_path = product_dir / self.filename
        
        # Step 3: Write content to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
        except Exception as e:
            return f"Error writing file: {str(e)}"
        
        # Step 4: Return success message
        return f"Successfully created document: {file_path}\n\nFile contains {len(self.content)} characters across {len(self.content.splitlines())} lines."


if __name__ == "__main__":
    # Test case
    tool = CreateDocument(
        product_name="Test Product",
        filename="test_document.md",
        content="""# Test Document

This is a test document to verify the CreateDocument tool works correctly.

## Section 1
Content for section 1.

## Section 2
Content for section 2.
"""
    )
    print(tool.run())

