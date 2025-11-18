from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from pathlib import Path

# Define the base mnt directory
# Use container path in production, local path for development
if os.path.exists("/app"):
    MNT_DIR = Path("/app/mnt")
else:
    # Local development - use path relative to project root
    MNT_DIR = Path(__file__).parent.parent.parent / "mnt"

class ListProducts(BaseTool):
    """
    Lists all products (folders) in the system that have strategy documents.
    Use this tool to see what products exist and can be worked on.
    Returns a list of product names that can be used with ListDocuments tools.
    """
    
    def run(self) -> str:
        """
        Lists all product folders that contain strategy_files directories.
        Returns a formatted list of products with document counts.
        """
        # Step 1: Check if mnt directory exists
        if not MNT_DIR.exists():
            return f"No products found. The mnt directory does not exist yet: {MNT_DIR}\n\nCreate your first product by providing product information to create foundational documents."
        
        if not MNT_DIR.is_dir():
            return f"Error: Path exists but is not a directory: {MNT_DIR}"
        
        # Step 2: Find all product folders (folders that have strategy_files subdirectory)
        try:
            products = []
            
            for item in sorted(MNT_DIR.iterdir()):
                if item.is_dir():
                    strategy_files_dir = item / "strategy_files"
                    if strategy_files_dir.exists() and strategy_files_dir.is_dir():
                        # Count markdown files in strategy_files
                        md_files = list(strategy_files_dir.glob("*.md"))
                        doc_count = len(md_files)
                        
                        # Get total size of all documents
                        total_size = sum(f.stat().st_size for f in md_files)
                        total_size_kb = total_size / 1024
                        
                        products.append({
                            'name': item.name,
                            'path': str(item),
                            'doc_count': doc_count,
                            'total_size_kb': total_size_kb,
                            'files': [f.name for f in md_files]
                        })
            
            # Step 3: Format output
            if not products:
                return f"No products found.\n\nThe mnt folder exists but contains no product folders with strategy documents yet.\n\nCreate your first product by providing product information to create foundational documents."
            
            output_lines = [
                f"Products found: {len(products)}",
                "",
            ]
            
            for idx, product in enumerate(products, 1):
                output_lines.append(f"{idx}. \"{product['name']}\" ({product['doc_count']} documents)")
            
            output_lines.append("")
            output_lines.append("To view details for a specific product, use:")
            output_lines.append("ListDocuments with product_name: [product_name]")
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"Error listing products: {str(e)}"


if __name__ == "__main__":
    # Test case - create some test products
    test_products = [
        ("Green_Tea_Extract", ["research_document.md", "avatar_sheet.md", "offer_brief.md"]),
        ("Acme_Widget_Pro", ["research_document.md", "avatar_sheet.md"]),
        ("Fitness_App", ["research_document.md"]),
    ]
    
    # Create test products
    for product_name, files in test_products:
        product_dir = MNT_DIR / product_name / "strategy_files"
        product_dir.mkdir(parents=True, exist_ok=True)
        
        for filename in files:
            content = f"# {filename.replace('.md', '').replace('_', ' ').title()}\n\nTest content for {product_name}\n" * 10
            with open(product_dir / filename, 'w') as f:
                f.write(content)
    
    # Test the tool
    tool = ListProducts()
    result = tool.run()
    print(result)
    
    # Cleanup
    for product_name, files in test_products:
        product_dir = MNT_DIR / product_name / "strategy_files"
        for filename in files:
            try:
                os.remove(product_dir / filename)
            except:
                pass
        try:
            product_dir.rmdir()
            (MNT_DIR / product_name).rmdir()
        except OSError:
            pass

