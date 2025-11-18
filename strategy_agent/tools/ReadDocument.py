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

class ReadDocument(BaseTool):
    """
    Reads the content of a markdown document from a product's strategy_files folder.
    Use this tool to review or reference previously created documents.
    """
    
    product_name: str = Field(
        ...,
        description="Name of the product this document belongs to (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract')."
    )
    
    filename: str = Field(
        ..., 
        description="Name of the file to read (e.g., 'brand_research_document.md'). Must end with .md extension."
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
    
    def run(self) -> str:
        """
        Reads and returns the content of the specified document.
        """
        # Step 1: Construct full file path
        product_dir = MNT_DIR / self.product_name / "strategy_files"
        file_path = product_dir / self.filename
        
        # Step 2: Check if file exists
        if not file_path.exists():
            # Provide helpful error message with available files
            if not product_dir.exists():
                return f"Error: Product folder does not exist: {product_dir}\n\nHave you created any documents for this product yet?"
            
            # List available files
            available_files = list(product_dir.glob("*.md"))
            if available_files:
                files_list = "\n- ".join([f.name for f in available_files])
                return f"Error: File '{self.filename}' not found in {product_dir}\n\nAvailable files:\n- {files_list}"
            else:
                return f"Error: File '{self.filename}' not found. The product folder exists but contains no documents."
        
        # Step 3: Read the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Step 4: Format the output with metadata
            line_count = content.count('\n') + 1
            char_count = len(content)
            word_count = len(content.split())
            
            header = f"""Document: {self.filename}
Product: {self.product_name}
Location: {file_path}
Stats: {line_count} lines, {word_count} words, {char_count} characters

{'=' * 60}

"""
            
            return header + content
            
        except UnicodeDecodeError:
            return f"Error: Unable to decode file {file_path}. It may be a binary file or have encoding issues."
        except Exception as e:
            return f"Error reading file: {str(e)}"


if __name__ == "__main__":
    # Test case - create a test document first
    test_product_name = "Test_Product"
    test_filename = "test_document.md"
    test_content = """# Test Document

This is a test document to verify the ReadDocument tool works correctly.

## Section 1
Content for section 1 with some details.

## Section 2
Content for section 2 with more information.

## Section 3
Final section with concluding remarks.
"""
    
    # Create test directory and file
    test_dir = MNT_DIR / test_product_name / "strategy_files"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file_path = test_dir / test_filename
    
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    # Test reading the file
    tool = ReadDocument(
        product_name=test_product_name,
        filename=test_filename
    )
    result = tool.run()
    print(result)
    
    # Test reading non-existent file
    print("\n" + "=" * 60 + "\n")
    tool2 = ReadDocument(
        product_name=test_product_name,
        filename="nonexistent.md"
    )
    result2 = tool2.run()
    print(result2)
    
    # Cleanup
    os.remove(test_file_path)
    try:
        test_dir.rmdir()
        (MNT_DIR / test_product_name).rmdir()
    except OSError:
        pass

