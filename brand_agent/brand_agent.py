from agents import ModelSettings
from openai.types.shared import Reasoning

from agency_swarm import Agent

brand_agent = Agent(
    name="BrandAgent",
    description="Responsible for creating ad scripts and copy based on client briefs and brand guidelines.",
    instructions="./instructions.md",
    tools_folder="./tools",
    files_folder="./files",
    model="gpt-5.2",
    model_settings=ModelSettings(
        reasoning=Reasoning(effort="medium", summary="auto"),
        truncation="auto",
    ),
)

if __name__ == "__main__":
    from dotenv import load_dotenv

    from agency_swarm import Agency

    load_dotenv()
    agency = Agency(brand_agent)
    agency.terminal_demo()
