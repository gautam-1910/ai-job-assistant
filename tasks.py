from crewai import Task
from agents import job_researcher, resume_tailor, cover_letter_writer

def create_tasks(job_role, skills, projects):

    research_task = Task(
        description=f"""Search for fresher {job_role} job openings in India. 
        Find at least 3 relevant companies hiring freshers.
        Focus on skills like: {skills}""",
        expected_output="A list of 3 companies with job title, required skills, and apply link if available.",
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