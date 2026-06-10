from crewai import Task
from agents import job_researcher, resume_tailor, cover_letter_writer

def create_tasks(job_role, skills, projects):

    research_task = Task(
    description=f"""Search for 3 fresher {job_role} job openings in India.
For each job return:
- Company name
- Job title  
- Direct apply URL (not job board homepage)
Skills to match: {skills}
Format each result as:
1. Company: [name] | Title: [title] | Apply: [direct url]
Be brief. No explanations.""",
    expected_output="3 jobs with company name, title, and direct apply link each.",
    agent=job_researcher
)

    tailor_task = Task(
        description=f"""Given the job role: {job_role}
        And the candidate's projects: {projects}
        And skills: {skills}
        Write a tailored resume summary (5-6 lines) highlighting relevant experience.""",
        expected_output="A tailored resume summary paragraph ready to paste into a resume.",
        agent=resume_tailor
    )

    cover_letter_task = Task(
        description=f"""Write a short cold email (under 150 words) for a fresher 
        applying for {job_role} role.
        Mention these projects: {projects}
        Mention these skills: {skills}
        Keep it professional and concise.""",
        expected_output="A ready-to-send cold email with subject line and body.",
        agent=cover_letter_writer
    )

    return [research_task, tailor_task, cover_letter_task]