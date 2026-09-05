import os
import time
import streamlit as st
from google import genai
from google.genai import errors

# Page Configuration
st.set_page_config(page_title="Professional Email Assistant", page_icon="✉️", layout="wide")

st.title("✉️ Professional AI Email Generator")
st.write("Generate tailored, professional emails in seconds using Gemini.")

# Read API Key securely from Streamlit Cloud Secrets or Environment Variables
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found! Please add it in Streamlit Cloud under Manage app -> Settings -> Secrets.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

if not api_key:
    st.error("⚠️ GEMINI_API_KEY environment variable not found!")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# Robust generation function with automatic retries and model fallbacks
def generate_with_retry(prompt):
    models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    
    for model_name in models_to_try:
        # Retry up to 3 times per model if 503 occurs
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text
            except errors.ServerError as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2 * (attempt + 1))  # Wait 2s, then 4s before retrying
                else:
                    raise e
            except Exception:
                break  # If model is unavailable/not found, jump to fallback model
                
    raise Exception("All models are currently busy. Please try again in a few moments.")

# Inputs in 2 columns
col1, col2 = st.columns(2)

with col1:
    recipient = st.text_input("Who Should I send the email to?", placeholder="e.g., Hiring Manager, Client, John Doe")
    purpose = st.text_input("Purpose of email", placeholder="e.g., Follow up on job application, Request a meeting")
    tone = st.selectbox("Tone of email", ["Professional", "Friendly", "Formal", "Persuasive", "Urgent", "Casual"])
    length = st.selectbox("Desired length", ["Short & Concise", "Medium", "Detailed"])

with col2:
    sender_info = st.text_input("Your information", placeholder="e.g., Jane Doe, Marketing Specialist")
    cta = st.text_input("Call to Action (CTA)", placeholder="e.g., Let's schedule a call this Thursday")
    key_points = st.text_area("Email key points or Message", placeholder="- Mention previous discussion\n- Highlight new proposal")

context = st.text_area("Add Context (Optional)", placeholder="Any additional background info...")

# Generate Initial Draft
if st.button("Generate Email 🚀", type="primary"):
    if not recipient or not purpose or not key_points:
        st.warning("Please fill in at least Recipient, Purpose, and Key Points.")
    else:
        prompt = f"""
        You are a professional email writing assistant.
        Generate a well-written email and 3 alternative subject lines based on the following details:

        - Recipient: {recipient}
        - Sender Info: {sender_info}
        - Tone: {tone}
        - Purpose: {purpose}
        - Length: {length}
        - Key Points: {key_points}
        - Call to Action: {cta}
        - Context: {context}

        Format output exactly as:

        PRIMARY SUBJECT: [Primary subject]

        ALTERNATIVE SUBJECTS:
        1. [Option 1]
        2. [Option 2]
        3. [Option 3]

        EMAIL BODY:
        [Complete email]
        """

        with st.spinner("Drafting your email..."):
            try:
                st.session_state["email_output"] = generate_with_retry(prompt)
            except Exception as err:
                st.error(f"⚠️ {str(err)}")

# Output & Improvement Section
if "email_output" in st.session_state:
    st.divider()
    st.subheader("📋 Generated Draft")
    
    st.code(st.session_state["email_output"], language="markdown")

    st.divider()
    st.subheader("✨ Improve Email")
    
    improvement_input = st.text_input(
        "How would you like to refine this email?", 
        placeholder="e.g., Make it more formal, fix typos, make it shorter"
    )

    if st.button("Apply Improvements 🪄"):
        if improvement_input:
            refine_prompt = f"""
            Refine and improve the following email output based on this feedback: "{improvement_input}"

            Original Draft:
            {st.session_state['email_output']}

            Keep the exact same response layout:
            PRIMARY SUBJECT:
            ALTERNATIVE SUBJECTS:
            EMAIL BODY:
            """
            with st.spinner("Improving email..."):
                try:
                    st.session_state["email_output"] = generate_with_retry(refine_prompt)
                    st.rerun()
                except Exception as err:
                    st.error(f"⚠️ {str(err)}")
