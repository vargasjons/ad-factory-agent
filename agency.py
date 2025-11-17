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
    
    # Handle brand colors section
    brand_colors_section = ""
    if config.get("brand_colors"):
        brand_colors_section = f"**Brand Colors:** {config['brand_colors']}"
    
    # Format the instructions with config values
    instructions = instructions.format(
        company_name=config.get("company_name", "Your Company"),
        industry=config.get("industry", "E-commerce"),
        brand_voice=config.get("brand_voice", "Professional and authentic"),
        visual_style_preferences=config.get("visual_style_preferences", "Authentic UGC aesthetic"),
        brand_colors_section=brand_colors_section,
        target_audience_demographics=config.get("target_audience_demographics", "Not specified"),
        target_audience_psychographics=config.get("target_audience_psychographics", "Not specified"),
        product_description=config.get("product_description", "Not specified"),
        product_category=config.get("product_category", "Consumer Products"),
        primary_business_goal=config.get("primary_business_goal", "Increase sales"),
        secondary_goals=config.get("secondary_goals", "Build brand awareness"),
        script_format_preferences=config.get("script_format_preferences", "Natural conversational flow")
    )
    
    return instructions


# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    # Create agents with config values inside the function
    # All agents use gpt-5.1 model for optimal performance
    strategy_agent = create_strategy_agent(
        model="gpt-5.1",
        reasoning_effort=config.get("strategy_agent_reasoning", "high")
    )
    brand_agent = create_brand_agent(
        model="gpt-5.1",
        reasoning_effort=config.get("brand_agent_reasoning", "medium")
    )
    ugc_agent = create_ugc_agent(
        model="gpt-5.1",
        reasoning_effort=config.get("ugc_agent_reasoning", "medium")
    )
    
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