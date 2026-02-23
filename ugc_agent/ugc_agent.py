import os

from agency_swarm import Agent, ModelSettings
from agency_swarm.tools import LoadFileAttachment
from openai.types.shared.reasoning import Reasoning

# Get the absolute path to the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))


def create_ugc_agent(model: str = "gpt-5.1", reasoning_effort: str = "medium") -> Agent:
    """Factory that returns a fresh UGCAgent instance.
    Use this in tests to avoid reusing a singleton across multiple agencies.
    
    Args:
        model: The LLM model to use for the agent
        reasoning_effort: The reasoning effort level (low, medium, high)
    """
    return Agent(
        name="UGCAgent",
        description="An agent that generates UGC-style advertisement videos and images.",
        instructions="instructions.md",
        tools_folder="./tools",
        tools=[LoadFileAttachment],
        model=model,
        model_settings=ModelSettings(
            reasoning=Reasoning(summary="auto", effort=reasoning_effort), truncation="auto"
        ),   
    )

if __name__ == "__main__":
    from dotenv import load_dotenv
    from agency_swarm import Agency

    load_dotenv()
    
    agent = create_ugc_agent()
    agency = Agency(agent)
    agency.terminal_demo()
