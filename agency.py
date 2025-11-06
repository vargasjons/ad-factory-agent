from dotenv import load_dotenv
from agency_swarm import Agency
from agency_swarm.tools.send_message import SendMessageHandoff

from strategy_agent import create_strategy_agent
from brand_agent import create_brand_agent
from ugc_agent import create_ugc_agent

load_dotenv()

# Create agents
strategy_agent = create_strategy_agent(model="gpt-5", reasoning_effort="high")
brand_agent = create_brand_agent(model="gpt-5", reasoning_effort="medium")
ugc_agent = create_ugc_agent(model="gpt-5", reasoning_effort="medium")

# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    agency = Agency(
        strategy_agent,  # Entry point - creates foundational documents
        communication_flows=[
            (strategy_agent > brand_agent > ugc_agent, SendMessageHandoff),  # Linear flow: Strategy → Script & Storyboard → Execution
        ],
        name="AdCreatorAgency",
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )

    return agency

if __name__ == "__main__":
    agency = create_agency()
    agency.terminal_demo()