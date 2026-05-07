import streamlit as st

from ai_engine import ask_ai
from tools import web_search, calculator
from memory import build_history

# ---------------- PAGE ----------------
st.set_page_config(page_title="NeuraAI", page_icon="🤖", layout="centered")


# ---------------- SESSION STATE ----------------
if "topics" not in st.session_state:
    st.session_state.topics = {}

if "active_topic" not in st.session_state:
    st.session_state.active_topic = None


# ---------------- HELPERS ----------------
def new_chat():
    st.session_state.active_topic = None


def delete_chat(topic):
    if topic in st.session_state.topics:
        del st.session_state.topics[topic]

    if st.session_state.active_topic == topic:
        st.session_state.active_topic = None


def generate_topic(text):
    return text[:45] + "..." if len(text) > 45 else text


# ---------------- SMART ROUTER ----------------
def route(q):
    q = q.lower().strip()

    if any(op in q for op in ["+", "-", "*", "/"]):
        return "calc"

    web_keywords = ["latest", "news", "who is", "what is", "when", "price", "weather"]
    if any(k in q for k in web_keywords):
        return "web"

    return "llm"


# ---------------- SIDEBAR ----------------
st.sidebar.title("🧠 NeuraAI")

if st.sidebar.button("➕ New Chat"):
    new_chat()

search = st.sidebar.text_input("🔍 Search topics")

st.sidebar.markdown("---")


# ---------------- CHAT LIST WITH DELETE ----------------
for topic in list(st.session_state.topics.keys()):

    if search and search.lower() not in topic.lower():
        continue

    col1, col2 = st.sidebar.columns([0.85, 0.15])

    with col1:
        if st.button("💬 " + topic, key=f"open_{topic}"):
            st.session_state.active_topic = topic

    with col2:
        if st.button("🗑", key=f"del_{topic}"):
            delete_chat(topic)
            st.rerun()


# ---------------- INPUT ----------------
query = st.chat_input("Ask anything...")


# ---------------- CREATE TOPIC ----------------
if query and st.session_state.active_topic is None:
    topic = generate_topic(query)
    st.session_state.active_topic = topic
    st.session_state.topics[topic] = []


# ---------------- HOME SCREEN ----------------
if not st.session_state.active_topic:
    st.markdown(
        """
        <div style="
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            height:70vh;
            text-align:center;
        ">
            <h1 style="font-size:42px;">🤖 NeuraAI</h1>
            <p style="color:gray; font-size:16px;">
                Ask anything to start your conversation
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- CHAT DISPLAY ----------------
if st.session_state.active_topic:

    topic = st.session_state.active_topic
    messages = st.session_state.topics[topic]

    st.title("🤖 NeuraAI")

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


# ---------------- MAIN LOGIC ----------------
if query and st.session_state.active_topic:

    topic = st.session_state.active_topic

    st.session_state.topics[topic].append({
        "role": "user",
        "content": query
    })

    tool = route(query)
    context = ""

    # ---------------- CALCULATOR ----------------
    if tool == "calc":
        result = calculator(query)

        st.session_state.topics[topic].append({
            "role": "assistant",
            "content": result
        })

        st.chat_message("assistant").write(result)
        st.stop()

    # ---------------- WEB SEARCH ----------------
    if tool == "web":
        with st.spinner("Searching web... 🌐"):
            context = web_search(query)

    # ---------------- MEMORY ----------------
    history_text = build_history(st.session_state.topics[topic])

    prompt = f"""
Conversation History:
{history_text}

Extra Context:
{context}

User Question:
{query}

Answer:
"""

    # ---------------- AI RESPONSE ----------------
    with st.spinner("Thinking... 🤖"):
        answer = ask_ai(prompt)

    st.session_state.topics[topic].append({
        "role": "assistant",
        "content": answer
    })

    st.chat_message("assistant").write(answer)