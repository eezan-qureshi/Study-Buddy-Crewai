"""Streamlit UI.  Run:  streamlit run app.py"""
import os
import streamlit as st
from study_crew import run_study_crew

st.set_page_config(page_title="Study Buddy (CrewAI)", page_icon="📚", layout="wide")
st.title("📚 Study Buddy")
st.caption("A team of 4 AI agents: Researcher → Explainer → Quiz Maker → Reviewer")

# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Settings")
    from config import get_api_key
    try:
        get_api_key()
        st.success("API key loaded from .env")
    except ValueError as e:
        st.error(str(e))
    level = st.selectbox("Student level", ["beginner", "intermediate", "advanced"])
    num_q = st.slider("Number of quiz questions", 3, 8, 5)
    st.markdown("---")
    st.markdown("**Agents**\n1. 🔎 Researcher (Wikipedia tool)\n2. ✍️ Explainer\n3. 📝 Quiz Maker (JSON + Pydantic)\n4. ✅ Reviewer (Word count tool)")

# ---------------- input ----------------
topic = st.text_input("What do you want to study?", placeholder="e.g. Neural networks, Photosynthesis, Mughal Empire")
go = st.button("🚀 Run the crew", type="primary", disabled=not topic.strip())

if go:
    try:
        with st.spinner("The agents are working... (this can take 30-60 seconds)"):
            st.session_state.result = run_study_crew(topic.strip(), level, num_q)
        st.session_state.topic = topic.strip()
        st.session_state.answers = {}
        st.session_state.submitted = False
    except ValueError as e:                      # missing key
        st.error(str(e))
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.info("If you see a 429 error, Groq's free limit is reached. Wait a minute and try again.")

# ---------------- output ----------------
res = st.session_state.get("result")
if res:
    st.subheader(f"Results for: {st.session_state.topic}")
    t1, t2, t3, t4 = st.tabs(["📖 Explanation", "📝 Quiz", "✅ Review", "🔍 Agent outputs"])

    with t1:
        st.write(res["explanation"])
        st.download_button("Download explanation", res["explanation"], file_name="explanation.txt")

    with t2:
        quiz = res["quiz"]
        if not quiz:
            st.warning("The Quiz Maker did not return valid JSON. Run again, or check the 'Agent outputs' tab.")
        else:
            for i, q in enumerate(quiz.questions):
                st.markdown(f"**Q{i+1}. {q.question}**")
                st.session_state.answers[i] = st.radio(
                    "Choose", q.options, index=None, key=f"q{i}", label_visibility="collapsed")
            if st.button("Submit answers"):
                st.session_state.submitted = True
            if st.session_state.get("submitted"):
                score = 0
                for i, q in enumerate(quiz.questions):
                    ok = st.session_state.answers.get(i) == q.options[q.answer_index]
                    score += ok
                    (st.success if ok else st.error)(
                        f"Q{i+1}: {'Correct' if ok else 'Wrong'} — answer: {q.options[q.answer_index]}. {q.explanation}")
                st.metric("Your score", f"{score} / {len(quiz.questions)}")

    with t3:
        (st.success if res["approved"] else st.warning)("APPROVED ✅" if res["approved"] else "The reviewer wants some fixes")
        st.write(res["review"])

    with t4:
        with st.expander("🔎 Researcher"): st.write(res["research"])
        with st.expander("✍️ Explainer"): st.write(res["explanation"])
        with st.expander("📝 Quiz Maker (raw JSON)"): st.code(res["quiz_raw"], language="json")
        with st.expander("✅ Reviewer"): st.write(res["review"])
        if res["tokens"]:
            st.caption(f"Token usage: {res['tokens']}")