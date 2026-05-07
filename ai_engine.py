import time
from google import genai
from groq import Groq
from config import GEMINI_API_KEY, GROQ_API_KEY


# ---------------- CLIENTS ----------------
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are a smart AI assistant like ChatGPT.

IMPORTANT STYLE RULES:
- First give a short simple explanation (1-2 lines).
- Then explain only important details (not everything).
- Avoid long technical dumps unless user asks.
- Do NOT include full code unless explicitly requested.
- Keep tone natural, smooth and conversational.
"""


# ---------------- GEMINI ----------------
def ask_gemini(prompt):
    try:
        res = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return res.text
    except Exception as e:
        print("Gemini error:", e)
        return None


# ---------------- GROQ ----------------
def ask_groq(prompt):
    if not groq_client:
        return None

    try:
        res = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        print("Groq error:", e)
        return None


# ---------------- PREPROCESSOR ----------------
def preprocess(prompt: str):
    p = prompt.lower()

    # FIX: YOLO handling
    if "yolo" in p:
        return "Explain YOLO (You Only Look Once) in a simple and clear way with examples."

    return prompt


# ---------------- MAIN AI FUNCTION ----------------
def ask_ai(prompt):

    # preprocess input
    prompt = preprocess(prompt)

    # final structured prompt (ChatGPT-like style)
    final_prompt = f"""
Explain clearly in a simple but accurate way.

First give a short precise definition.
Then explain with a simple real-life analogy.

User question:
{prompt}
"""

    # try Gemini first
    result = ask_gemini(final_prompt)
    if result:
        return result

    time.sleep(1)

    # fallback Groq
    result = ask_groq(final_prompt)
    if result:
        return result

    return "❌ AI unavailable right now. Please try again."