from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Literal
from pathlib import Path

class ReadFoundationalDoc(BaseTool):
    """
    Reads the content of a foundational strategy document.
    These are reference templates and guides used for creating strategy documents.
    Use this tool to access methodology, frameworks, and templates for strategic planning.
    """
    
    document_name: Literal[
        "Avatar_Sheet_Template",
        "Necessary_Beliefs", 
        "Offer_Brief_Template",
        "Research_Part_1",
        "Research_Part_2"
    ] = Field(
        ...,
        description=(
            "Name of the foundational document to read:\n"
            "- Avatar_Sheet_Template: Template for creating customer avatar sheets\n"
            "- Necessary_Beliefs: Framework for identifying beliefs needed for product success\n"
            "- Offer_Brief_Template: Template for creating comprehensive offer briefs\n"
            "- Research_Part_1: Research methodology and framework (Part 1)\n"
            "- Research_Part_2: Research methodology and framework (Part 2)"
        )
    )
    
    def run(self) -> str:
        """
        Reads and returns the content of the specified foundational document.
        """
        # Step 1: Define the base path to foundational documents
        # These documents are stored in the strategy_agent/files directory
        base_path = Path(__file__).parent.parent / "files"
        
        # Step 2: Construct full file path with .md extension
        file_path = base_path / f"{self.document_name}.md"
        
        # Step 3: Check if file exists
        if not file_path.exists():
            return f"Error: Foundational document '{self.document_name}.md' not found at {file_path}"
        
        # Step 4: Read the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Step 5: Format the output with metadata
            line_count = content.count('\n') + 1
            char_count = len(content)
            word_count = len(content.split())
            
            header = f"""Foundational Document: {self.document_name}
Type: Reference Template/Framework
Location: {file_path}
Stats: {line_count} lines, {word_count} words, {char_count} characters

{'=' * 80}

"""
            
            return header + content
            
        except UnicodeDecodeError:
            return f"Error: Unable to decode file {file_path}. It may have encoding issues."
        except Exception as e:
            return f"Error reading foundational document: {str(e)}"


if __name__ == "__main__":
    # Test case 1: Read Avatar_Sheet_Template
    print("Test 1: Reading Avatar_Sheet_Template")
    print("=" * 80)
    tool1 = ReadFoundationalDoc(document_name="Avatar_Sheet_Template")
    result1 = tool1.run()
    # Print first 500 characters to verify it works
    print(result1[:500] + "...\n")
    
    # Test case 2: Read Necessary_Beliefs
    print("\nTest 2: Reading Necessary_Beliefs")
    print("=" * 80)
    tool2 = ReadFoundationalDoc(document_name="Necessary_Beliefs")
    result2 = tool2.run()
    print(result2[:500] + "...\n")
    
    # Test case 3: Read Offer_Brief_Template
    print("\nTest 3: Reading Offer_Brief_Template")
    print("=" * 80)
    tool3 = ReadFoundationalDoc(document_name="Offer_Brief_Template")
    result3 = tool3.run()
    print(result3[:500] + "...\n")
    
    # Test case 4: Read Research_Part_1
    print("\nTest 4: Reading Research_Part_1")
    print("=" * 80)
    tool4 = ReadFoundationalDoc(document_name="Research_Part_1")
    result4 = tool4.run()
    print(result4[:500] + "...\n")
    
    # Test case 5: Read Research_Part_2
    print("\nTest 5: Reading Research_Part_2")
    print("=" * 80)
    tool5 = ReadFoundationalDoc(document_name="Research_Part_2")
    result5 = tool5.run()
    print(result5[:500] + "...\n")
    
    print("All tests completed successfully!")

