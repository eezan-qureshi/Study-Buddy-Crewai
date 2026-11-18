"""The crew: 4 agents work one after another (sequential).
Researcher -> Explainer -> Quiz Maker -> Reviewer.
Used by both main.py (terminal) and app.py (Streamlit)."""
import json, re
from typing import List
from pydantic import BaseModel, field_validator
from crewai import Agent, Task, Crew, Process

from config import get_llm
from tools import wikipedia_summary, word_count


# ---------- Pydantic models: we check the Quiz Maker's JSON in code ----------
class Question(BaseModel):
    question: str
    options: List[str]
    answer_index: int          # 0..3
    explanation: str

    @field_validator("options")
    @classmethod
    def four_options(cls, v):
        if len(v) != 4:
            raise ValueError("a question needs exactly 4 options")
        return v

    @field_validator("answer_index")
    @classmethod
    def index_in_range(cls, v):
        if not 0 <= v <= 3:
            raise ValueError("answer_index must be 0, 1, 2 or 3")
        return v


class Quiz(BaseModel):
    questions: List[Question]


def parse_json(text: str):
    """Models sometimes wrap JSON in ```json fences. Remove them, then parse."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)


def build_crew(llm, with_quiz_retry_hint=""):
    researcher = Agent(
        role="Researcher", goal="Find the key facts about a topic",
        backstory="You are careful. You use the Wikipedia tool first and give only facts you are sure about, as short bullet points.",
        tools=[wikipedia_summary], llm=llm, max_iter=5, allow_delegation=False)
    explainer = Agent(
        role="Explainer", goal="Turn notes into a clear explanation for the student's level",
        backstory="You are a patient teacher. You write simple English with one everyday example. You never add facts that are not in the notes.",
        llm=llm, allow_delegation=False)
    quiz_maker = Agent(
        role="Quiz Maker", goal="Write fair multiple-choice questions from the explanation",
        backstory="You are an exam setter. Every question has exactly 4 options and exactly one correct answer. You reply only with JSON.",
        llm=llm, allow_delegation=False)
    reviewer = Agent(
        role="Reviewer", goal="Check the explanation and the quiz and approve them or list fixes",
        backstory="You are strict but fair. You check the explanation length with the Word count tool. You reply APPROVED, or a short list of fixes.",
        tools=[word_count], llm=llm, max_iter=5, allow_delegation=False)

    research_task = Task(
        description="Collect 5 key facts about {topic} for a {level} student.",
        expected_output="5 short bullet points.", agent=researcher)
    explain_task = Task(
        description="Write an explanation of {topic} for a {level} student in about 120 words, using ONLY the research facts. End with one everyday example.",
        expected_output="One clear explanation of about 120 words.", agent=explainer, context=[research_task])
    quiz_task = Task(
        description=("Write {num_questions} multiple-choice questions about {topic} using ONLY the explanation. " + with_quiz_retry_hint),
        expected_output=('Reply ONLY with JSON like: {{"questions": [{{"question": "...", "options": ["A","B","C","D"], '
                         '"answer_index": 0, "explanation": "..."}}]}}. answer_index is a whole number 0 to 3.'),
        agent=quiz_maker, context=[explain_task])
    review_task = Task(
        description="Review the explanation and the quiz. Count the words of the explanation with the tool. Reply APPROVED, or list what to fix.",
        expected_output="APPROVED, or a short list of fixes.", agent=reviewer, context=[explain_task, quiz_task])

    return Crew(agents=[researcher, explainer, quiz_maker, reviewer],
                tasks=[research_task, explain_task, quiz_task, review_task],
                process=Process.sequential, verbose=False)


def run_study_crew(topic: str, level: str = "beginner", num_questions: int = 5, api_key: str = None):
    """Runs the crew and returns a dict the UI can show."""
    llm = get_llm(api_key)
    inputs = {"topic": topic, "level": level, "num_questions": num_questions}

    quiz, hint, result = None, "", None
    for attempt in range(2):                      # if the JSON is broken, try once more
        result = build_crew(llm, hint).kickoff(inputs=inputs)
        try:
            quiz = Quiz(**parse_json(result.tasks_output[2].raw))
            break
        except Exception as e:
            hint = f"IMPORTANT: your last JSON was invalid ({e}). Return valid JSON only."

    outs = [o.raw for o in result.tasks_output]
    return {
        "research": outs[0], "explanation": outs[1], "quiz": quiz,
        "quiz_raw": outs[2], "review": outs[3],
        "approved": "APPROVED" in outs[3].upper(),
        "tokens": getattr(result, "token_usage", None),
    }
