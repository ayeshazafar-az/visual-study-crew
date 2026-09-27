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
st.set_page_config(page_title="Multi-Agent Study Forge", page_icon="🎓", layout="wide")

# Custom CSS for a beautiful, highly animated Dark UI
st.markdown("""
    <style>
    /* 1. Deep Slate Navy Background (NO Black) */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #0b1120, #0f172a, #1e293b, #0f172a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. Slide-up Fade Entry Animation */
    [data-testid="stMainBlockContainer"] {
        animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        transform: translateY(30px);
        padding-top: 4rem !important; 
    }
    @keyframes slideUpFade {
        to { opacity: 1; transform: translateY(0); }
    }

    /* 3. Gorgeous Emerald/Ocean Header */
    .main-header {
        font-size: 3.8rem;
        font-weight: 900;
        margin-bottom: 0px;
        background: linear-gradient(90deg, #10b981, #0ea5e9, #10b981);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textShimmer 4s linear infinite;
        line-height: 1.2;
    }
    @keyframes textShimmer {
        to { background-position: 200% center; }
    }

    /* 4. Sleek Sub Header */
    .sub-header {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 30px;
        font-weight: 400;
    }

    /* 5. Premium Glowing Emerald Button */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #0ea5e9 100%);
        color: #ffffff !important;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        padding: 15px 30px;
        border: none;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
        background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
    }
    .stButton>button:active {
        transform: translateY(1px);
    }

    /* 6. Slate Frosted Glass Input Container */
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ System Status")
    st.info("A multi-agent assembly line that transforms raw concepts and documents into beautifully illustrated study guides.")
    st.markdown("---")
    
    # API Validation Indicator
    api_key = os.environ.get("GEMINI_API_KEY", "").replace('"', '').replace("'", "").strip()
    if api_key:
        st.success("🟢 API Connected")
    else:
        st.error("🔴 API Key Missing")
        
    st.markdown("---")
    st.markdown("**Active Agents:**")
    st.markdown("👨‍🏫 **Professor:** Concept Analysis")
    st.markdown("🎨 **Visualizer:** Mnemonic Design")
    st.markdown("📝 **Quizmaster:** Assessment Compilation")

# --- MAIN UI ---
st.markdown('<p class="main-header">🎓 Multi-Agent Study Forge</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Choose your input method below to generate a comprehensive study guide.</p>', unsafe_allow_html=True)

# Create unified input container
study_material = ""

st.markdown("### Prepare Your Study Material")
with st.container(border=True):
    topic_input = st.text_area("Context or Topic (Optional)", placeholder="e.g., Explain the Architecture of a CPU...", help="Describe the topic you want to learn, or provide context for your uploaded file.", label_visibility="collapsed")
    
    uploaded_file = st.file_uploader("Upload a PDF or Image (Optional)", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    if file_ext == "pdf":
        with st.spinner("Extracting text from PDF..."):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                extracted_text = ""
                for page in pdf_reader.pages:
                    if page.extract_text():
                        extracted_text += page.extract_text() + "\n"
                
                if len(extracted_text) > 15000:
                    extracted_text = extracted_text[:15000] + "\n...[Content Truncated for Processing]..."
                    st.warning("⚠️ Document is very long. Analyzing the first ~15,000 characters.")
                
                study_material += f"Document Content:\n{extracted_text}\n\n"
                st.success(f"📄 PDF '{uploaded_file.name}' extracted successfully!")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
                
    elif file_ext in ["png", "jpg", "jpeg"]:
        temp_path = "temp_upload.png"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        
        study_material += f"Image Reference: [IMAGE_PATH] {temp_path}\n\n"
        st.success(f"🖼️ Image '{uploaded_file.name}' readied for the Professor!")

if topic_input:
    study_material += f"User Instructions/Topic:\n{topic_input}\n\n"

study_material = study_material.strip()
# If empty, study_material will equal an empty string. The "if not study_material" check handles this.

st.markdown("---")

# --- EXECUTION ORCHESTRATOR ---
if st.button("🚀 Generate Visual Study Guide", use_container_width=True):
    if not study_material:
        st.error("⚠️ Please enter a topic or upload a document first.")
    else:
        # Dynamic UI status container
        with st.status("🤖 Orchestrating the Crew...", expanded=True) as status:
            try:
                st.write("👨‍🏫 Handing material to **The Professor** for analysis...")
                tasks = create_study_tasks(study_material)
                
                st.write("🎨 Instructing **The Visualizer** to design concept art...")
                st.write("📝 **The Quizmaster** is standing by to compile the final markdown...")
                
                # Assemble the Crew (verbose=False keeps terminal clean)
                study_crew = Crew(
                    agents=[professor, visualizer, quizmaster],
                    tasks=tasks,
                    verbose=False 
                )
                
                # Execute Workflow with Fallback Logic for 503 errors
                max_retries = 2
                
                for attempt in range(max_retries):
                    try:
                        result = study_crew.kickoff()
                        break  # If successful, break out of the retry loop
                    except Exception as e:
                        if "503" in str(e) and attempt < max_retries - 1:
                            st.warning(f"⚠️ High API Demand (503). Switching to Fallback Pro Model...")
                            # Swap out the models for all agents
                            professor.llm = gemini_fallback_llm
                            visualizer.llm = gemini_fallback_llm
                            quizmaster.llm = gemini_fallback_llm
                            
                            # Reconstruct the crew
                            study_crew = Crew(
                                agents=[professor, visualizer, quizmaster],
                                tasks=tasks,
                                verbose=False 
                            )
                        else:
                            raise e  # Propagate the error if retries are exhausted or it's a different error
                
                status.update(label="✅ Study Guide Complete!", state="complete", expanded=False)
                
                # Render Final Output
                st.markdown("---")
                st.subheader("📖 Your Custom Study Guide")
                if hasattr(result, 'raw'):
                    st.markdown(result.raw)
                else:
                    st.markdown(result)
                    
            except Exception as e:
                status.update(label="❌ Generation Failed", state="error")
                st.error(f"An error occurred: {str(e)}")