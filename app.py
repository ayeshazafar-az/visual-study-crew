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

# Custom CSS for "Nebula Glass" Dashboard
st.markdown("""
    <style>
    /* 1. Global Background */
    [data-testid="stAppViewContainer"] {
        background-color: #0b0914;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(123, 44, 191, 0.2), transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(0, 198, 255, 0.15), transparent 40%);
        color: #ffffff;
    }

    /* 2. Top Padding Fix */
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }

    /* 3. Glassmorphism Containers (applying to border=True containers) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(22, 18, 43, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(0, 198, 255, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Remove padding inside metric/action cards */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0.5rem !important;
    }

    /* 4. Chat Bubbles */
    [data-testid="stChatMessage"] {
        background: rgba(30, 26, 59, 0.5);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 10px 20px;
        margin-bottom: 15px;
    }

    /* 5. Headings and Text */
    h1, h2, h3, h4, p, span {
        color: #e2def2 !important;
    }
    
    /* Fix hr */
    hr {
        border-color: rgba(255,255,255,0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- APP LAYOUT ---

# Top Bar / Left Sidebar Area
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='background: linear-gradient(90deg, #00C6FF, #FF007A); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Nexus OS</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✨ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("### Quick Actions")
    st.button("📁 Upload Context", use_container_width=True)
    st.button("⚙️ Settings", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Active Agents")
    st.markdown("🟢 **Professor** (Idle)")
    st.markdown("🟢 **Visualizer** (Idle)")
    st.markdown("🟢 **Quizmaster** (Idle)")
    
    st.markdown("---")
    st.markdown("*(Powered by CrewAI & Gemini)*")

# Main Screen Router
if len(st.session_state.messages) == 0:
    # --- EMPTY STATE DASHBOARD ---
    st.markdown("""
        <h1 style='font-size: 3.5rem; font-weight: 800; background: linear-gradient(90deg, #00C6FF, #7B2CBF, #FF007A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px;'>
            Good Evening, Explorer.
        </h1>
        <p style='font-size: 1.2rem; color: #B1A9D4; margin-bottom: 3rem;'>
            Build, analyze, and automate learning with multi-agent AI.
        </p>
    """, unsafe_allow_html=True)
    
    # Grid of Suggested Actions
    st.markdown("### Suggested Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎓 Blueprint a Syllabus\n\nGenerate a full learning plan.", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Please generate a complete syllabus and step-by-step learning plan for my given topic."})
            st.rerun()
    with col2:
        if st.button("🖼️ Analyze Diagram\n\nUpload an image to break it down.", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Please analyze the attached context/image and break down the architecture step-by-step."})
            st.rerun()
    with col3:
        if st.button("📝 Create Flashcards\n\nExtract key terms for review.", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Please extract the key concepts and terms from my context and generate formatted study flashcards."})
            st.rerun()
    with col4:
        if st.button("🧩 Interactive Quiz\n\nTest your knowledge on a topic.", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Please generate a comprehensive, interactive-style quiz (multiple choice and short answer) based on my context."})
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
            
    # Secondary Grid (Agent Status and Diagnostics)
    eco1, eco2 = st.columns([2, 1])
    
    with eco1:
        st.markdown("### System Diagnostics")
        with st.container(border=True):
            st.markdown("⚡ **Core Engine:** Gemini 1.5 Flash (Active)")
            st.markdown("🧩 **Orchestrator:** CrewAI (Online)")
            st.markdown("🌐 **Render Engine:** Graphviz DOT (Connected)")
    
    with eco2:
        st.markdown("### API Health")
        with st.container(border=True):
            api_key = os.environ.get("GEMINI_API_KEY", "")
            if api_key:
                st.markdown("<h2 style='color: #10b981; margin:0;'>OK</h2>", unsafe_allow_html=True)
                st.markdown("<small style='color:#a1a1aa;'>Secure Connection</small>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color: #ef4444; margin:0;'>FAIL</h2>", unsafe_allow_html=True)
                st.markdown("<small style='color:#a1a1aa;'>API Key Missing</small>", unsafe_allow_html=True)
                
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

else:
    # --- CHAT UI ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)
            
    st.write("") # Spacer

# --- FLOATING INPUT PIPELINE ---
with st.expander("📎 Attach Context (PDF or Image) to your next message"):
    uploaded_file = st.file_uploader("Upload material", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Ask a question to Nova (Your AI Assistant)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun() # Immediately rerun to show the empty state vanishing and the chat appending

# Processing logic (Triggers after rerun clears the dashboard)
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]
    
    study_material = ""
    chat_history = ""
    for m in st.session_state.messages[:-1]:
        chat_history += f"{m['role'].capitalize()}: {m['content']}\n\n"
        
    if chat_history:
        study_material += f"--- PREVIOUS CONVERSATION HISTORY ---\n{chat_history}\n--- END HISTORY ---\n\n"

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

    study_material += f"Latest User Prompt:\n{prompt}\n\n"
    study_material = study_material.strip()

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
                
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                
            except Exception as e:
                status.update(label="❌ Generation Failed", state="error")
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})