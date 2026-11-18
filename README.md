# Study Buddy: CrewAI + Streamlit

Type a topic. A crew of 4 agents researches it, explains it, makes a quiz, and a reviewer checks the work.
Python 3.10-3.13 needed (CrewAI does not support 3.14 yet).

## Files
| File | What it does |
|---|---|
| `config.py` | Groq LLM setup (key from `.env` or the sidebar) |
| `tools.py` | Tools: Wikipedia summary, Word count |
| `study_crew.py` | 4 agents, 4 tasks, sequential crew, Pydantic quiz check |
| `main.py` | Run in the terminal |
| `app.py` | Streamlit web app |

## Setup (VS Code terminal)
```
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and paste your Groq key. In VS Code: Ctrl+Shift+P > Python: Select Interpreter > `.venv`.

## Run
```
streamlit run app.py          # web app
python main.py "Photosynthesis"   # terminal version
```
