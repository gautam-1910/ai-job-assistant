from crewai import Crew, Process
from agents import job_researcher, resume_tailor, cover_letter_writer
from tasks import create_tasks

# ---- YOUR DETAILS ---- #
job_role = "Python Developer"
skills = "Python, Flask, MongoDB, YOLOv11, OpenCV, Node.js"
projects = "SPARC (PPE detection using YOLOv11 on Raspberry Pi), Grocery List Expiry Tracker (OCR + MongoDB + Gemini chatbot)"
# ---------------------- #

tasks = create_tasks(job_role, skills, projects)

crew = Crew(
    agents=[job_researcher, resume_tailor, cover_letter_writer],
    tasks=tasks,
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
print("\n\n========================")
print("FINAL OUTPUT:")
print(result)