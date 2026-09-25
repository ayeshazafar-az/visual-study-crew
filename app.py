import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
from crewai import Crew
from agents import professor, visualizer, quizmaster
from tasks import create_study_tasks

# Force reload from .env
load_dotenv(override=True)

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Multi-Agent Study Forge", page_icon="🎓", layout="wide")

# Custom CSS for a polished look
st.markdown("""
    <style>
    .stButton>button {
        background-color: #2E86C1;
        color: white;
        font-size: 18px;
        border-radius: 8px;
        padding: 15px 24px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1B4F72;
    }
    .main-header {
        font-size: 2.8rem;
        color: #1B4F72;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5D6D7E;
        margin-bottom: 30px;
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

# Create Tabs for different input methods
tab1, tab2, tab3 = st.tabs(["📝 Text Topic", "📄 Upload PDF", "🖼️ Upload Image"])

study_material = None

with tab1:
    st.markdown("### Enter a Subject to Learn")
    topic_input = st.text_input("Topic", placeholder="e.g., The Architecture of a CPU, Photosynthesis, The French Revolution...", label_visibility="collapsed")
    if topic_input:
        study_material = topic_input

with tab2:
    st.markdown("### Upload a Document")
    uploaded_file = st.file_uploader("Upload a PDF file to extract core study materials", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                extracted_text = ""
                for page in pdf_reader.pages:
                    if page.extract_text():
                        extracted_text += page.extract_text() + "\n"
                
                # Truncate text to prevent overloading the LLM token limit
                if len(extracted_text) > 15000:
                    extracted_text = extracted_text[:15000] + "\n...[Content Truncated for Processing]..."
                    st.warning("⚠️ Document is very long. Analyzing the first ~15,000 characters.")
                
                study_material = f"Based on the following extracted document text, generate a study guide:\n\n{extracted_text}"
                st.success(f"📄 PDF '{uploaded_file.name}' extracted successfully!")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

with tab3:
    st.markdown("### Upload an Educational Image")
    uploaded_image = st.file_uploader("Upload a diagram, notes screenshot, or visual aid", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if uploaded_image:
        # Save temp image
        temp_path = "temp_upload.png"
        with open(temp_path, "wb") as f:
            f.write(uploaded_image.read())
        
        study_material = f"[IMAGE_PATH] {temp_path}"
        st.success(f"🖼️ Image '{uploaded_image.name}' readied for the Professor!")

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
                
                # Execute Workflow
                result = study_crew.kickoff()
                
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