import os
import litellm
from dotenv import load_dotenv
from crewai import Agent, LLM
from crewai_tools import SerperDevTool

load_dotenv()

litellm.drop_params = True
litellm.cache = None
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

search_tool = SerperDevTool()

# Patch: strip cache_breakpoint from messages before Groq call
original_completion = litellm.completion

def patched_completion(*args, **kwargs):
    if "messages" in kwargs:
        for msg in kwargs["messages"]:
            msg.pop("cache_breakpoint", None)
            msg.pop("cache_control", None)
    return original_completion(*args, **kwargs)

litellm.completion = patched_completion

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

job_researcher = Agent(
    role="Job Market Researcher",
    goal="Find relevant fresher job openings based on the candidate's skills",
    backstory="You are an expert job market analyst specializing in finding opportunities for fresh graduates in tech.",
    tools=[search_tool],
    llm=llm,
    verbose=True
)

resume_tailor = Agent(
    role="Resume Tailor",
    goal="Tailor the candidate's resume summary and skills to match job descriptions",
    backstory="You are an expert resume writer who highlights the right skills and projects.",
    llm=llm,
    verbose=True
)

cover_letter_writer = Agent(
    role="Cover Letter Writer",
    goal="Write a short compelling cold email for the job",
    backstory="You are a professional writer who crafts concise impactful cold emails.",
    llm=llm,
    verbose=True
)