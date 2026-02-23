from agents import ModelSettings, WebSearchTool
from openai.types.shared import Reasoning

from agency_swarm import Agent

strategy_agent = Agent(
    name="StrategyAgent",
    description="Performs market research and creates the foundational documents that guide ad creation.",
    instructions="./instructions.md",
    tools_folder="./tools",
    files_folder="./files",
    tools=[WebSearchTool()],
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
    agency = Agency(strategy_agent)
    agency.terminal_demo()
