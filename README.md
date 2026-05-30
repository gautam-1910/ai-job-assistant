# AI Job Application Assistant

A multi-agent AI system that automates job search, 
resume tailoring, and cold email generation for fresher job seekers.

## 🚀 Features
- Searches for relevant fresher job openings in India
- Tailors resume summary based on candidate's projects and skills
- Generates a professional cold email for job applications

## 🛠️ Tech Stack
- **Framework:** CrewAI
- **LLM:** Groq (llama-3.1-8b-instant)
- **Search:** Serper API
- **Language:** Python

## 🤖 Agents
| Agent | Role |
|-------|------|
| Job Market Researcher | Searches for relevant fresher job openings |
| Resume Tailor | Tailors resume summary to match job description |
| Cover Letter Writer | Writes a concise cold email for the job |

## 📁 Project Structure

## ⚙️ Setup
1. Clone the repo
2. Create virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate
```
3. Install dependencies
```bash
   pip install crewai crewai-tools python-dotenv litellm
```
4. Add API keys to `.env`

5. Run
```bash
   python main.py
```

## 🔑 API Keys Required
- [Groq](https://console.groq.com) — Free
- [Serper](https://serper.dev) — Free tier available

## ⚠️ Known Limitations
- Optimized for single-user demo
- Groq free tier: 6,000 TPM, 1,000 requests/day
- Production scaling requires Groq Developer tier

## 🗺️ Roadmap
- [ ] FastAPI backend
- [ ] React frontend
- [ ] MongoDB integration
- [ ] PDF resume upload and parsing
- [ ] Multi-user support
- [ ] Multiple resume profiles per user

## 📜 License
MIT