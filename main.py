"""Run the crew in the terminal (no Streamlit):  python main.py "Neural networks" """
import sys
from study_crew import run_study_crew

topic = sys.argv[1] if len(sys.argv) > 1 else "Neural networks"
r = run_study_crew(topic, level="beginner", num_questions=3)
print("\n=== EXPLANATION ===\n", r["explanation"])
print("\n=== QUIZ ===")
if r["quiz"]:
    for i, q in enumerate(r["quiz"].questions, 1):
        print(f"{i}. {q.question}")
        for j, o in enumerate(q.options):
            print("   ", "ABCD"[j], o)
        print("   Answer:", "ABCD"[q.answer_index], "-", q.explanation)
else:
    print("Quiz JSON was invalid:\n", r["quiz_raw"])
print("\n=== REVIEW ===\n", r["review"])
print("\nTokens:", r["tokens"])
