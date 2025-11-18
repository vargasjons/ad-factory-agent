from dotenv import load_dotenv
from agency_swarm import Agency
from agency_swarm.tools.send_message import SendMessageHandoff
import os

from strategy_agent import create_strategy_agent
from brand_agent import create_brand_agent
from ugc_agent import create_ugc_agent

# Import onboarding configuration
from onboarding_config import config

load_dotenv()


def render_shared_instructions():
    """Dynamically render shared_instructions.md with config values"""
    from onboarding_config import config
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    instructions_path = os.path.join(current_dir, "shared_instructions.md")
    
    with open(instructions_path, "r", encoding="utf-8") as file:
        instructions = file.read()
    
    # Format the instructions with config values
    instructions = instructions.format(
        company_name=config.get("company_name", "Your Company"),
        visual_brand_guidelines=config.get("visual_brand_guidelines", "Authentic UGC aesthetic, natural lighting, relatable settings")
    )
    
    return instructions


# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    # Create agents with config values inside the function
    # All agents use gpt-5.1 model with medium reasoning for optimal performance
    strategy_agent = create_strategy_agent(model="gpt-5.1")
    brand_agent = create_brand_agent(model="gpt-5.1")
    ugc_agent = create_ugc_agent(model="gpt-5.1")
    
    agency = Agency(
        strategy_agent,  # Entry point - creates foundational documents
        brand_agent,
        ugc_agent,
        communication_flows=[
            (strategy_agent > brand_agent > ugc_agent, SendMessageHandoff),  # Linear flow: Strategy → Script & Storyboard → Execution
        ],
        name="AdCreatorAgency",
        shared_instructions=render_shared_instructions(),  # Dynamic instructions from config
        load_threads_callback=load_threads_callback,
    )

    return agency

if __name__ == "__main__":
    agency = create_agency()
    agency.terminal_demo()