# app.py
import random
import streamlit as st
from ss_data import revision_data
from quiz_data import quiz_questions

# ---------- Page setup & playful theme ----------
st.set_page_config(
    page_title="SST 10 Revision Mate",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Simple vibrant CSS
st.markdown("""
<style>
/* playful header gradient */
.header {
  background: linear-gradient(90deg,#9B5DE5,#FF6B6B,#FFD93D);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
}
/* card styling */
.block {
  background: #fffdf6;
  border: 2px solid #ffe9a8;
  border-radius: 18px;
  padding: 1rem 1.2rem;
  box-shadow: 0 6px 18px rgba(255,215,64,.25);
}
small.note { color:#555; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header'>📚 SST 10 Revision Mate</h1>", unsafe_allow_html=True)
st.caption("Made by Harshita for Class 10 students")

# ---------- Sidebar navigation ----------
mode = st.sidebar.radio("Choose Mode", ["📖 Revision", "📝 Quiz"])
st.sidebar.write("---")
st.sidebar.write("Tip: Works on phones too. Use landscape for quiz.")

# ---------- Revision Mode ----------
if mode == "📖 Revision":
    st.subheader("Revision")
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("Subject", list(revision_data.keys()))
    with col2:
        chapter_names = list(revision_data[subject].keys())
        chapter = st.selectbox("Chapter", chapter_names)

    st.markdown("### " + chapter)
    st.markdown("<div class='block'>", unsafe_allow_html=True)

    section = revision_data[subject][chapter]
    # Show sections nicely
    if "Important Dates" in section:
        with st.expander("📅 Important Dates", expanded=True):
            for item in section["Important Dates"]:
                st.markdown(f"- {item}")
    if "Key Events" in section:
        with st.expander("⭐ Key Events", expanded=True):
            for item in section["Key Events"]:
                st.markdown(f"- {item}")
    if "Important Facts" in section:
        with st.expander("📌 Important Facts", expanded=True):
            for item in section["Important Facts"]:
                st.markdown(f"- {item}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.info("Use the dropdowns to switch chapters quickly.")

# ---------- Quiz Mode ----------
else:
    st.subheader("Quiz")
    chapter = st.selectbox("Select Chapter", list(quiz_questions.keys()))

    # Filter valid questions
    raw_qlist = quiz_questions[chapter].get("questions", [])
    qlist = [
        q for q in raw_qlist
        if isinstance(q, dict) and all(k in q for k in ("question", "options", "answer"))
    ]

    if not qlist:
        st.error("❌ No valid questions found for this chapter. Please check quiz_data.py.")
        st.stop()

    shuffle_on = st.checkbox("Shuffle questions", value=True)

    # Initialize session state for quiz
    if "quiz" not in st.session_state:
        st.session_state.quiz = {}
    if chapter not in st.session_state.quiz:
        st.session_state.quiz[chapter] = {
            "order": list(range(len(qlist))),
            "idx": 0,
            "score": 0,
            "last_answer_correct": None,
            "finished": False
        }
        if shuffle_on:
            random.shuffle(st.session_state.quiz[chapter]["order"])

    qstate = st.session_state.quiz[chapter]

    # Controls row
    c1, c2, c3 = st.columns(3)
    if c1.button("🔁 Restart"):
        st.session_state.quiz[chapter] = {
            "order": list(range(len(qlist))),
            "idx": 0,
            "score": 0,
            "last_answer_correct": None,
            "finished": False
        }
        if shuffle_on:
            random.shuffle(st.session_state.quiz[chapter]["order"])
        st.rerun()
    c2.metric("Score", f"{qstate['score']} / {len(qlist)}")
    c3.metric("Question", f"{min(qstate['idx']+1, len(qlist))} / {len(qlist)}")

    # If finished, show result
    if qstate["finished"]:
        st.success(f"🎉 Quiz complete! Final Score: {qstate['score']} / {len(qlist)}")
        st.stop()

    # Current question
    current_q_index = qstate["order"][qstate["idx"]]
    q = qlist[current_q_index]
    st.markdown("### " + q["question"])

    # Use a unique key per question index so selection resets each time
    choice = st.radio(
        "Choose one:",
        q["options"],
        index=None,
        key=f"opt_{chapter}_{qstate['idx']}"
    )

    # Feedback area
    if qstate["last_answer_correct"] is True:
        st.success("✅ Correct!")
    elif qstate["last_answer_correct"] is False:
        st.error(f"❌ Incorrect. Correct answer: **{q['answer']}**")

    # Buttons
    b1, b2 = st.columns(2)
    if b1.button("Submit"):
        if choice is None:
            st.warning("Please select an option.")
        else:
            if choice == q["answer"]:
                qstate["score"] += 1
                qstate["last_answer_correct"] = True
            else:
                qstate["last_answer_correct"] = False

    if b2.button("Next ➡️"):
        # Move to next question if submitted (or allow skipping)
        if qstate["idx"] + 1 < len(qlist):
            qstate["idx"] += 1
            qstate["last_answer_correct"] = None
            st.rerun()
        else:
            qstate["finished"] = True
            st.rerun()
