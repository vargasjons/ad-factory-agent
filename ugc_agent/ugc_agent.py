from agents import ModelSettings
from openai.types.shared import Reasoning

from agency_swarm import Agent

ugc_agent = Agent(
    name="UGCAgent",
    description="An agent that generates UGC-style advertisement videos and images.",
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
    agency = Agency(ugc_agent)
    agency.terminal_demo()
