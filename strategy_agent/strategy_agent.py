import os
from agency_swarm import Agent, ModelSettings, WebSearchTool
from openai.types.shared.reasoning import Reasoning

current_dir = os.path.dirname(os.path.abspath(__file__))

def create_strategy_agent(model: str = "gpt-5.1", reasoning_effort: str = "high") -> Agent:
    """
    Creates the StrategyAgent - the entry point for the agency.
    
    This agent conducts deep research and creates the foundational documents
    that guide all subsequent work (Avatar Sheet, Necessary Beliefs, Offer Brief, Research).
    """
    return Agent(
        name="StrategyAgent",
        description="Performs market research and creates the foundational documents that guide ad creation.",
        instructions="instructions.md",
        model=model,
        tools_folder="./tools",
        files_folder="./files",
        tools=[WebSearchTool()],
        model_settings=ModelSettings(
            reasoning=Reasoning(summary="auto", effort=reasoning_effort), 
            truncation="auto"
        ),   
    )

if __name__ == "__main__":
    from dotenv import load_dotenv
    from agency_swarm import Agency
    load_dotenv()
    agent = create_strategy_agent()
    agency = Agency(agent)
    agency.terminal_demo()

