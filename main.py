from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
import agentops
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, tool, BaseTool
# from infobip_channels.sms.channel import SMSChannel
import os
from langchain_community.utilities.infobip import InfobipAPIWrapper
from scripts.ingest import encode_image, get_file_names_in_directory, create_image_message
from crewai_tools import SerperDevTool


infobip = InfobipAPIWrapper()
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.environ["REAL_OPENAI_API_KEY"],
    base_url="https://api.openai.com/v1"
)


agentops.init()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", dimensions=1024, api_key=os.environ["REAL_OPENAI_API_KEY"], base_url="https://api.openai.com/v1")
db = Chroma("images_with_meta", embeddings, "chroma")


def get_park_list():
    parks = db.similarity_search("grand canyon", 5)
    test = [p.metadata["location"] for p in parks]
    print(set(test))


@tool("Send SMS")
def send_sms_message_tool(message: str) -> str:
    """Sends an SMS message to the user."""
    infobip.run(
        to=os.environ["PHONE_NUMBER"],
        body=message,
        sender="parks",
        channel="sms",
    )
    return "successfully sent message"


@tool("Retrieve Parks")
def park_retrieval_tool() -> set[str]:
    """Retrieves a set of parks based on user uploaded images."""
    user_folder = 'imgs/user'
    user_files = get_file_names_in_directory(user_folder)
    image_data = [encode_image(f"imgs/user/{fn}") for fn in user_files]
    inputs = [create_image_message(img_data) for img_data in image_data]
    results = llm.batch(inputs, return_exceptions=True)
    retrieved_parks = [db.similarity_search(r.content, k=5) for r in results]
    all_parks = [p.metadata["location"]
                 for parks in retrieved_parks for p in parks]
    return set(all_parks)


search_tool = SerperDevTool()


def main():
    # Define your agents
    researcher = Agent(
        role="Researcher",
        goal="Conduct thorough research on the climate of the park and look for any relevant news such as poor air quality or other warnings.",
        backstory="You are a detailed researcher that will look into the climate of the park.",
        allow_delegation=False,
        tools=[search_tool]
    )

    social_worker = Agent(
        role="The Absolute BEST Psychologist",
        goal="Perform sentiment analysis on the user's message to determine what kind of adventure they want.",
        backstory="You are THE ABSOLUTE BEST social worker!!! You think deeply and analyze the user message to extract any sentiments that could indicate what kind of adventure they want.",
        allow_delegation=False,
    )

    retriever = Agent(
        role="User Preference Retriever",
        goal="Retrieve user preferences for parks.",
        backstory="You are a retriever that queries the database for parks that match the user preferences.",
        tools=[park_retrieval_tool],
        allow_delegation=False,
    )

# Define your task
    recommend = Task(
        description="Recommend one park for the user to go to. The first element in the set is the top result!",
        expected_output="5 bullet points, each with a paragraph and accompanying notes.",
    )

    sentiment_analysis = Task(
        description="Obtain sentiment of the user to understand what kind of adventure they want to have.",
        expected_output="A detailed summary that influences what park to recommend the user.",
        # agent=researcher,
        # human_input=True
    )

    retrieval_task = Task(
        description="Retrieve a set of parks based on user uploaded images.",
        expected_output="A set of parks that the user would like to visit.",
    )

    send_sms_task = Task(
        description="Send the recommended parks and a concise summary of the reasons for the recommendation to the user. Also be sure to send weather information and any relevant current news about the park.",
        expected_output="A successful response from the messager agent indicating that a SMS message has been sent."
    )

    research_climate = Task(
        description="Send the recommended park and a concise summary of the reasons for the recommendation to the user. Also be sure to send weather information and any relevant current news about the park.",
        expected_output="Understand the current weather conditions of the park in mind, the current date is July 27th, 2024."
    )

    messager = Agent(
        role="Messenger",
        goal="You are a messenger agent that sends cheerful and concise messages to the user. You are responsible for contacting the user with tool.",
        backstory="You are a messenger agent who is terse.",
        allow_delegation=False,
        tools=[send_sms_message_tool]
    )

# Define the manager agent
    manager = Agent(
        role="Project Manager",
        goal="Efficiently manage the crew and ensure high-quality task completion.",
        backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
    )


# Instantiate your crew with a custom manager
    crew = Crew(
        agents=[retriever, researcher, messager],
        # agents=[researcher, writer, messager, retriever],
        # tasks=[task, send_sms_task],
        tasks=[retrieval_task, research_climate, send_sms_task],
        manager_agent=manager,
        process=Process.hierarchical,
    )


# Start the crew's work
    result = crew.kickoff()
    print(result)


if __name__ == "__main__":
    main()
    agentops.end_session("Success")
