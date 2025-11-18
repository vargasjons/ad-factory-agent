import os
from typing import Optional
from pathlib import Path

from agency_swarm.tools import BaseTool
from pydantic import Field, field_validator

# Define the base mnt directory
# Use container path in production, local path for development
if os.path.exists("/app"):
    MNT_DIR = Path("/app/mnt")
else:
    # Local development - use path relative to project root
    MNT_DIR = Path(__file__).parent.parent.parent / "mnt"


class EditDocument(BaseTool):
    """
    Performs exact string replacements in strategy documents organized by product.

    Usage:
    - When editing text, ensure you preserve the exact indentation (tabs/spaces) as it appears in the file.
    - The edit will FAIL if `old_string` is not unique in the file. Either provide a larger string with more surrounding context to make it unique or use `replace_all` to change every instance of `old_string`.
    - Use `replace_all` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.
    """

    product_name: str = Field(
        ...,
        description="Name of the product this document is for (e.g., 'Acme_Widget_Pro', 'Green_Tea_Extract'). Used to locate the product-specific sub-folder."
    )
    
    filename: str = Field(
        ..., 
        description="Name of the file to edit (e.g., 'brand_research_document.md'). Must end with .md extension."
    )
    
    old_string: str = Field(..., description="The text to replace")
    new_string: str = Field(
        ...,
        description="The text to replace it with (must be different from old_string). Provide empty string if you want to delete the text.",
    )
    replace_all: Optional[bool] = Field(
        False, description="Replace all occurrences of old_string (default false)"
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

    def run(self):
        try:
            # Step 1: Construct full file path from product name and filename
            product_dir = MNT_DIR / self.product_name / "strategy_files"
            file_path = product_dir / self.filename
            
            # Step 2: Validate that old_string and new_string are different
            if self.old_string == self.new_string:
                return "Error: old_string and new_string must be different"

            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File does not exist: {file_path}"

            # Check if it's a file
            if not os.path.isfile(file_path):
                return f"Error: Path is not a file: {file_path}"

            # Read the file
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except UnicodeDecodeError:
                return f"Error: Unable to decode file {file_path}. It may be a binary file."

            # Check if old_string exists in the file
            if self.old_string not in content:
                return f"Error: String to replace not found in file.\\nString: {repr(self.old_string)}"

            # Count occurrences
            occurrences = content.count(self.old_string)

            # If there are multiple occurrences and replace_all is False, require uniqueness
            if occurrences > 1 and not self.replace_all:
                # Build a preview of first two matches
                previews = []
                start_idx = 0
                for _ in range(2):
                    idx = content.find(self.old_string, start_idx)
                    if idx == -1:
                        break
                    a = max(0, idx - 30)
                    b = min(len(content), idx + len(self.old_string) + 30)
                    previews.append("..." + content[a:b] + "...")
                    start_idx = idx + len(self.old_string)
                preview_block = "\n".join(previews)
                return (
                    f"Error: String appears {occurrences} times in file. Either provide a larger string with more "
                    f"surrounding context to make it unique or use replace_all=True to change every instance.\n"
                    f"First matches:\n{preview_block}"
                )

            # Perform the replacement
            if self.replace_all:
                new_content = content.replace(self.old_string, self.new_string)
                replacement_count = occurrences
            else:
                # Replace only the first occurrence
                new_content = content.replace(self.old_string, self.new_string, 1)
                replacement_count = 1

            # Write the modified content back to the file
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(new_content)

                # Create a short diff-like preview snippet (first and last replacement context)
                preview_lines = []
                old_preview_indices = []
                start_idx = 0
                while True:
                    idx = content.find(self.old_string, start_idx)
                    if idx == -1:
                        break
                    old_preview_indices.append(idx)
                    start_idx = idx + len(self.old_string)
                    if not self.replace_all and len(old_preview_indices) >= 1:
                        break

                def make_context(src: str, idx: int, needle: str, repl: str) -> str:
                    a = max(0, idx - 30)
                    b = min(len(src), idx + len(needle) + 30)
                    before = src[a:idx]
                    after = src[idx + len(needle) : b]
                    return f"...{before}[{needle}->{repl}]{after}..."

                if old_preview_indices:
                    first_idx = old_preview_indices[0]
                    preview_lines.append(
                        make_context(
                            content, first_idx, self.old_string, self.new_string
                        )
                    )
                    if self.replace_all and len(old_preview_indices) > 1:
                        last_idx = old_preview_indices[-1]
                        if last_idx != first_idx:
                            preview_lines.append(
                                make_context(
                                    content, last_idx, self.old_string, self.new_string
                                )
                            )

                preview = "\n".join(preview_lines) if preview_lines else ""

                msg = f"Successfully replaced {replacement_count} occurrence(s) in {file_path}"
                if preview:
                    msg += f"\nPreview:\n{preview}"
                return msg

            except PermissionError:
                return f"Error: Permission denied writing to file: {file_path}"
            except Exception as e:
                return f"Error writing to file: {str(e)}"

        except Exception as e:
            return f"Error during edit operation: {str(e)}"


if __name__ == "__main__":
    # Test the tool - create a test file first
    test_product_name = "Test_Product"
    test_filename = "test_document.md"
    test_content = """# Test Document

This is a test file.
Line 2 has some text.
Line 3 has the same text.
Final line."""

    # Create test directory and file
    test_dir = MNT_DIR / test_product_name / "strategy_files"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file_path = test_dir / test_filename
    
    with open(test_file_path, "w") as f:
        f.write(test_content)

    print("Original content:")
    print(test_content)
    print("\n" + "=" * 50 + "\n")

    # Test single replacement
    tool = EditDocument(
        product_name=test_product_name,
        filename=test_filename,
        old_string="some text",
        new_string="REPLACED TEXT"
    )
    result = tool.run()
    print("Single replacement result:")
    print(result)

    # Read and show the modified content
    with open(test_file_path, "r") as f:
        modified_content = f.read()
    print("\nModified content:")
    print(modified_content)

    # Test replace_all
    tool2 = EditDocument(
        product_name=test_product_name,
        filename=test_filename,
        old_string="text",
        new_string="content",
        replace_all=True,
    )
    result2 = tool2.run()
    print("\n" + "=" * 50 + "\n")
    print("Replace all result:")
    print(result2)

    # Read and show final content
    with open(test_file_path, "r") as f:
        final_content = f.read()
    print("\nFinal content:")
    print(final_content)

    # Cleanup
    os.remove(test_file_path)
    # Clean up the test directory structure
    try:
        test_dir.rmdir()
        (MNT_DIR / test_product_name).rmdir()
    except OSError:
        # Directories may not be empty or may not exist
        pass
