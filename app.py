import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
from crewai import Crew
from agents import professor, visualizer, quizmaster, gemini_fallback_llm
from tasks import create_study_tasks

# Force reload from .env
load_dotenv(override=True)

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Study Forge AI", page_icon="🎓", layout="wide")

# Custom CSS for "Nebula Glass" (Deep Indigo & Holographic Magenta) + Chat Bubbles
st.markdown("""
    <style>
    /* 1. Deep Indigo with Holographic Ambient Glows */
    [data-testid="stAppViewContainer"] {
        background-color: #121026;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(255, 0, 122, 0.15), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(0, 198, 255, 0.15), transparent 25%);
    }

    /* 2. Slide-up Entry Animation */
    [data-testid="stMainBlockContainer"] {
        animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        transform: translateY(30px);
        padding-top: 4rem !important; 
    }
    @keyframes slideUpFade {
        to { opacity: 1; transform: translateY(0); }
    }

    /* 3. Electric Blue to Hot Pink Gradient Header */
    .main-header {
        font-size: 3.8rem;
        font-weight: 900;
        margin-bottom: 0px;
        background: linear-gradient(90deg, #00C6FF, #7B2CBF, #FF007A);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textShimmer 5s linear infinite;
        letter-spacing: -1px;
        line-height: 1.2;
    }
    @keyframes textShimmer {
        to { background-position: 200% center; }
    }

    /* 4. Soft Lilac Sub Header */
    .sub-header {
        font-size: 1.15rem;
        color: #B1A9D4;
        margin-bottom: 30px;
        font-weight: 400;
    }

    /* 5. Glowing Chat Avatars & Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(30, 26, 59, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 10px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    [data-testid="stChatMessage"] * {
        color: #ffffff !important;
    }
    
    /* 6. Expanders Styling (Attachments) */
    [data-testid="stExpander"] {
        background: rgba(30, 26, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px;
    }
    p {
        color: #B1A9D4;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MAIN UI ---
st.markdown('<p class="main-header">🎓 Study Forge Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your intelligent multi-agent conversational researcher. Ask me anything.</p>', unsafe_allow_html=True)

# --- CHAT HISTORY RENDER LOOP ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

st.write("") # Spacer

# --- ATTACHMENT PIPELINE ---
with st.expander("📎 Attach Context (PDF or Image) to your next message"):
    uploaded_file = st.file_uploader("Upload material to give the Professor context", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")

# --- CONVERSATIONAL INPUT WAIT ---
if prompt := st.chat_input("Ask a question, request a diagram, or provide instructions..."):
    # 1. Store and display user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Extract Document/Context if attached
    study_material = ""
    
    # Prepend History for Agent memory
    chat_history = ""
    for m in st.session_state.messages[:-1]: # Don't include the immediate prompt we just added
        chat_history += f"{m['role'].capitalize()}: {m['content']}\n\n"
        
    if chat_history:
        study_material += f"--- PREVIOUS CONVERSATION HISTORY ---\n{chat_history}\n--- END HISTORY ---\n\n"

    # Add File Data
    if uploaded_file:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext == "pdf":
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                extracted_text = ""
                for page in pdf_reader.pages:
                    if page.extract_text():
                        extracted_text += page.extract_text() + "\n"
                
                if len(extracted_text) > 15000:
                    extracted_text = extracted_text[:15000] + "\n...[Content Truncated]..."
                
                study_material += f"Attached Document Content:\n{extracted_text}\n\n"
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
                
        elif file_ext in ["png", "jpg", "jpeg"]:
            temp_path = "temp_upload.png"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            study_material += f"Image Reference: [IMAGE_PATH] {temp_path}\n\n"

    # Add Latest Prompt
    study_material += f"Latest User Prompt:\n{prompt}\n\n"
    study_material = study_material.strip()

    # 3. Execute Orchestrator
    with st.chat_message("assistant"):
        with st.status("🧠 Agents are thinking...", expanded=True) as status:
            try:
                st.write("👨‍🏫 Professor analyzing context & history...")
                tasks = create_study_tasks(study_material)
                
                study_crew = Crew(
                    agents=[professor, visualizer, quizmaster],
                    tasks=tasks,
                    verbose=False 
                )
                
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        result = study_crew.kickoff()
                        break 
                    except Exception as e:
                        if "503" in str(e) and attempt < max_retries - 1:
                            st.warning(f"⚠️ High API Demand (503). Switching to Fallback Pro Model...")
                            professor.llm = gemini_fallback_llm
                            visualizer.llm = gemini_fallback_llm
                            quizmaster.llm = gemini_fallback_llm
                            
                            study_crew = Crew(agents=[professor, visualizer, quizmaster], tasks=tasks, verbose=False)
                        else:
                            raise e 
                
                status.update(label="✅ Response Generated", state="complete", expanded=False)
                
                final_text = result.raw if hasattr(result, 'raw') else str(result)
                st.markdown(final_text, unsafe_allow_html=True)
                
                # 4. Save to Memory
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                
            except Exception as e:
                status.update(label="❌ Generation Failed", state="error")
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})