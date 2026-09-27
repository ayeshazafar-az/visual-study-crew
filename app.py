import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import professor, visualizer, quizmaster, gemini_fallback_llm, gemini_llm
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
    
    /* 6. Interactive Flashcards */
    .flashcard-wrapper {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
        margin-top: 20px;
    }
    .flip-card {
        background-color: transparent;
        width: 300px;
        height: 200px;
        perspective: 1000px;
    }
    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        cursor: pointer;
    }
    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }
    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .flip-card-front {
        background: rgba(30, 26, 59, 0.8);
        backdrop-filter: blur(12px);
    }
    .flip-card-back {
        background: linear-gradient(135deg, #7B2CBF, #FF007A);
        transform: rotateY(180deg);
    }
    .flip-card h3 {
        color: #00C6FF !important;
        margin: 0;
    }
    .flip-card-back p {
        color: white !important;
        font-size: 0.95rem;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- PDF EXPORT ENGINE ---
def generate_pdf_bytes(md_content):
    from fpdf import FPDF
    import markdown
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    # Strip simple non-latin chars and emojis for basic FPDF 
    clean_md = md_content.encode('latin-1', 'ignore').decode('latin-1')
    html = markdown.markdown(clean_md)
    try:
        pdf.write_html(html)
    except Exception as e:
        pdf.multi_cell(0, 8, text=f"-- PDF Html Warning --\n\n{clean_md}")
    return bytes(pdf.output())

# --- SESSION MEMORY ---
def save_history(messages):
    # Dummy function to maintain compatibility if called
    pass

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_action" not in st.session_state:
    st.session_state.selected_action = None

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
    st.markdown("### Export Session")
    
    if len(st.session_state.messages) > 0:
        session_md = "# Study Session Export\n\n"
        for msg in st.session_state.messages:
            role_title = "User" if msg["role"] == "user" else "Assistant"
            session_md += f"### {role_title}\n\n{msg['content']}\n\n"
            
        master_pdf_data = generate_pdf_bytes(session_md)
        st.download_button("⬇️ Download Full Chat as PDF", data=master_pdf_data, file_name=f"Full_Session_Export.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.markdown("<small style='color:#a1a1aa;'>Start chatting to generate an export.</small>", unsafe_allow_html=True)
        
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
    import datetime
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
        
    st.markdown(f"""
        <h1 style='font-size: 3.5rem; font-weight: 800; background: linear-gradient(90deg, #00C6FF, #7B2CBF, #FF007A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px;'>
            {greeting}, Explorer.
        </h1>
        <p style='font-size: 1.2rem; color: #B1A9D4; margin-bottom: 3rem;'>
            Build, analyze, and automate learning with multi-agent AI.
        </p>
    """, unsafe_allow_html=True)
    
    # Action Selection Router
    if not st.session_state.selected_action:
        # Grid of Suggested Actions
        st.markdown("### Suggested Actions")
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            with st.container(border=True):
                if st.button("🎓 Blueprint a Syllabus", use_container_width=True):
                    st.session_state.selected_action = "syllabus"
                    st.rerun()
                st.markdown("<div style='text-align:center; font-size:0.8rem; color:#a1a1aa; margin-top:-10px; padding-bottom:10px;'>Generate a full learning plan.</div>", unsafe_allow_html=True)
                
        with row1_col2:
            with st.container(border=True):
                if st.button("🖼️ Analyze Diagram", use_container_width=True):
                    st.session_state.selected_action = "default"
                    st.rerun()
                st.markdown("<div style='text-align:center; font-size:0.8rem; color:#a1a1aa; margin-top:-10px; padding-bottom:10px;'>Upload an image to break it down.</div>", unsafe_allow_html=True)
                
        row2_col1, row2_col2 = st.columns(2)
        
        with row2_col1:
            with st.container(border=True):
                if st.button("📝 Create Flashcards", use_container_width=True):
                    st.session_state.selected_action = "flashcards"
                    st.rerun()
                st.markdown("<div style='text-align:center; font-size:0.8rem; color:#a1a1aa; margin-top:-10px; padding-bottom:10px;'>Extract key terms for review.</div>", unsafe_allow_html=True)
                
        with row2_col2:
            with st.container(border=True):
                if st.button("🧩 Interactive Quiz", use_container_width=True):
                    st.session_state.selected_action = "quiz"
                    st.rerun()
                st.markdown("<div style='text-align:center; font-size:0.8rem; color:#a1a1aa; margin-top:-10px; padding-bottom:10px;'>Test your knowledge on a topic.</div>", unsafe_allow_html=True)
                
        st.markdown("<br>", unsafe_allow_html=True)
        
    else:
        # Intermediate Context Form
        action_map = {
            "syllabus": ("🎓 Blueprint a Syllabus", "[MODE:syllabus] Please generate a complete syllabus and step-by-step learning plan using this context."),
            "default": ("🖼️ Analyze Diagram", "[MODE:default] Please analyze the provided context/image and break down the architecture step-by-step."),
            "flashcards": ("📝 Create Flashcards", "[MODE:flashcards] Please extract the key concepts from this context and generate formatted study flashcards."),
            "quiz": ("🧩 Interactive Quiz", "[MODE:quiz] Please generate a comprehensive, interactive-style quiz (multiple choice and short answer) based on this context.")
        }
        
        act_title, act_prompt = action_map.get(st.session_state.selected_action, ("", ""))
        
        with st.container(border=True):
            st.markdown(f"### {act_title}")
            st.markdown("<p style='color:#a1a1aa;'>Please provide the source material you would like the AI agents to process.</p>", unsafe_allow_html=True)
            
            pasted_text = st.text_area("Paste text context (Optional):", height=150)
            qa_upload = st.file_uploader("Upload Image/PDF (Optional)", type=["pdf", "png", "jpg", "jpeg"], key="qa_upload")
            
            cola, colb = st.columns([1, 3])
            with cola:
                if st.button("⬅️ Back"):
                    st.session_state.selected_action = None
                    st.rerun()
            with colb:
                if st.button("✨ Generate Now", use_container_width=True):
                    file_ref = ""
                    if qa_upload:
                        ext = qa_upload.name.split('.')[-1].lower()
                        if ext == "pdf":
                            import PyPDF2
                            try:
                                pdf_reader = PyPDF2.PdfReader(qa_upload)
                                extracted = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                                file_ref = f"\n\nAttached PDF Content:\n{extracted[:15000]}"
                            except Exception as e:
                                pass
                        else:
                            temp_path = "temp_upload.png" 
                            with open(temp_path, "wb") as f:
                                f.write(qa_upload.read())
                            file_ref = f"\n\nImage Reference: [IMAGE_PATH] {temp_path}"
                            
                    payload = f"{act_prompt}\n\nContext Provided:\n{pasted_text}{file_ref}"
                    st.session_state.messages.append({"role": "user", "content": payload})
                    save_history(st.session_state.messages)
                    st.session_state.selected_action = None
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
    import re
    # --- CHAT UI ---

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            clean_display = re.sub(r"\[MODE:(.*?)\]\s*", "", msg["content"])
            st.markdown(clean_display, unsafe_allow_html=True)
            
            if msg["role"] == "assistant":
                pdf_data = generate_pdf_bytes(clean_display)
                st.download_button("⬇️ Download as PDF", data=pdf_data, file_name=f"StudyForge_Export.pdf", mime="application/pdf", key=f"dl_pdf_{i}")
            
    st.write("") # Spacer

# --- FLOATING INPUT PIPELINE ---
with st.expander("📎 Attach Context (PDF or Image) to your next message"):
    uploaded_file = st.file_uploader("Upload material", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Ask a question to Nova (Your AI Assistant)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)
    st.rerun() # Immediately rerun to show the empty state vanishing and the chat appending

# Processing logic (Triggers after rerun clears the dashboard)
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    raw_prompt = st.session_state.messages[-1]["content"]
    
    import re
    mode = "default"
    mode_match = re.search(r"\[MODE:(.*?)\]\s*", raw_prompt)
    if mode_match:
        mode = mode_match.group(1)
        clean_prompt = raw_prompt.replace(mode_match.group(0), "")
        st.session_state.messages[-1]["content"] = clean_prompt
        save_history(st.session_state.messages)
        prompt = clean_prompt
    else:
        prompt = raw_prompt
    
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
                st.write(f"👨‍🏫 Orchestrating learning tasks (Mode: {mode.upper()})...")
                tasks = create_study_tasks(study_material, mode=mode)
                
                study_crew = Crew(
                    agents=[professor, visualizer, quizmaster],
                    tasks=tasks,
                    process=Process.hierarchical,
                    manager_llm=gemini_llm,
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
                            study_crew = Crew(
                                agents=[professor, visualizer, quizmaster], 
                                tasks=tasks, 
                                process=Process.hierarchical,
                                manager_llm=gemini_fallback_llm,
                                verbose=False
                            )
                        else:
                            raise e 
                
                status.update(label="✅ Response Generated", state="complete", expanded=False)
                
                final_text = result.raw if hasattr(result, 'raw') else str(result)
                st.markdown(final_text, unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                save_history(st.session_state.messages)
                
            except Exception as e:
                status.update(label="❌ Generation Failed", state="error")
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_msg}"})
                save_history(st.session_state.messages)