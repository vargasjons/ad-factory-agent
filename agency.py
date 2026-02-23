import os

from brand_agent import brand_agent
from dotenv import load_dotenv
from strategy_agent import strategy_agent
from ugc_agent import ugc_agent

from agency_swarm import Agency

load_dotenv()


def render_shared_instructions():
    """Dynamically render shared_instructions.md with config values."""
    try:
        from onboarding_config import config
    except ImportError:
        config = {}

    current_dir = os.path.dirname(os.path.abspath(__file__))
    instructions_path = os.path.join(current_dir, "shared_instructions.md")

    with open(instructions_path, encoding="utf-8") as file:
        instructions = file.read()

    instructions = instructions.format(
        company_name=config.get("company_name", "Your Company"),
        visual_brand_guidelines=config.get(
            "visual_brand_guidelines",
            "Authentic UGC aesthetic, natural lighting, relatable settings",
        ),
    )

    return instructions


# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    agency = Agency(
        strategy_agent,
        communication_flows=[
            (strategy_agent, brand_agent),
            (brand_agent, ugc_agent),
        ],
        name="UGC AD Factory",
        shared_instructions=render_shared_instructions(),
        load_threads_callback=load_threads_callback,
    )

    return agency


if __name__ == "__main__":
    agency = create_agency()
    agency.terminal_demo()
