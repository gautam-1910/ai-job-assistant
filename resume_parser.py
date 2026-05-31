import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes"""
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def parse_resume_with_llm(raw_text: str, llm) -> dict:
    """Use LLM to extract skills and projects from resume text"""
    prompt = f"""
    Extract the following from this resume text:
    1. Technical skills (comma separated)
    2. Projects (comma separated project names with one line description)
    3. Job role the candidate is targeting

    Resume text:
    {raw_text[:3000]}

    Respond in this exact format:
    SKILLS: skill1, skill2, skill3
    PROJECTS: project1 - description, project2 - description
    JOB_ROLE: role name
    """
    
    response = llm.call([{"role": "user", "content": prompt}])
    
    skills = ""
    projects = ""
    job_role = ""
    
    for line in response.split("\n"):
        if line.startswith("SKILLS:"):
            skills = line.replace("SKILLS:", "").strip()
        elif line.startswith("PROJECTS:"):
            projects = line.replace("PROJECTS:", "").strip()
        elif line.startswith("JOB_ROLE:"):
            job_role = line.replace("JOB_ROLE:", "").strip()
    
    return {
        "skills": skills,
        "projects": projects,
        "job_role": job_role
    }