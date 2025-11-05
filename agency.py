from dotenv import load_dotenv
from agency_swarm import Agency

from ad_factory_agent import create_ad_factory_agent

# import asyncio

load_dotenv()

ad_creator_agent = create_ad_factory_agent(model="gpt-5", reasoning_effort="medium")
# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    agency = Agency(
        ad_creator_agent,
        name="AdCreatorAgency", # don't forget to rename your agency!
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )

    return agency

if __name__ == "__main__":
    agency = create_agency()

    # test 1 message
    # async def main():
    #     response = await agency.get_response("Hello, how are you?")
    #     print(response)
    # asyncio.run(main())

    # run in terminal
    agency.terminal_demo()