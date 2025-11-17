import os

from agency_swarm import Agent, ModelSettings
from openai.types.shared.reasoning import Reasoning

# Get the absolute path to the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))


def create_brand_agent(model: str = "gpt-5.1", reasoning_effort: str = "medium") -> Agent:
    """Factory that returns a fresh BrandAgent instance.
    Use this in tests to avoid reusing a singleton across multiple agencies.
    """
    return Agent(
        name="BrandAgent",
        description="Responsible for creating ad scripts and copy based on client briefs and brand guidelines.",
        instructions="instructions.md",
        model=model,
        model_settings=ModelSettings(
            reasoning=Reasoning(summary="auto", effort=reasoning_effort), truncation="auto"
        ),   
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    from agency_swarm import Agency

    load_dotenv()
    
    agent = create_brand_agent()
    agency = Agency(agent)
    agency.terminal_demo()
