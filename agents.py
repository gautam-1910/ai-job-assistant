import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import search_tool

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = LLM(
    model="groq/llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
    cache=False
)

job_researcher = Agent(
    role="Job Market Researcher",
    goal="Find relevant fresher job openings based on the candidate's skills",
    backstory="""You are an expert job market analyst who specializes 
    in finding the best job opportunities for fresh graduates in tech.""",
    tools=[search_tool],
    llm=llm,
    verbose=True
)

resume_tailor = Agent(
    role="Resume Tailor",
    goal="Tailor the candidate's resume summary and skills to match job descriptions",
    backstory="""You are an expert resume writer who knows how to highlight 
    the right skills and projects to match specific job descriptions.""",
    llm=llm,
    verbose=True
)

cover_letter_writer = Agent(
    role="Cover Letter Writer",
    goal="Write a short, compelling cold email or cover letter for the job",
    backstory="""You are a professional writer who crafts concise, 
    impactful cover letters and cold emails that get responses.""",
    llm=llm,
    verbose=True
)