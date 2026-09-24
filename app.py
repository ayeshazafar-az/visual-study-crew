import streamlit as st
import os
from dotenv import load_dotenv
from crewai import Crew
from agents import professor, visualizer, quizmaster
from tasks import create_study_tasks

# Load environment variables from .env file
load_dotenv()

# Streamlit Page Configuration
st.set_page_config(page_title="Visual StudyCrew", page_icon="📚", layout="centered")

st.title("📚 Visual StudyCrew")
st.markdown("Enter a topic below, and a team of AI agents will research, visualize, and generate a complete study guide.")

# Ensure API key is set
if not os.environ.get("GEMINI_API_KEY"):
    st.warning("⚠️ GEMINI_API_KEY is not set in the .env file.")
    st.stop()

# User Input
topic_input = st.text_input("What do you want to learn about?", placeholder="e.g., How Neural Networks work, Photosynthesis, The French Revolution")

if st.button("Generate Study Guide"):
    if not topic_input:
        st.error("Please enter a topic to study.")
    else:
        with st.spinner("The Crew is analyzing, designing, and compiling your study guide... This usually takes 30-60 seconds."):
            try:
                # 1. Fetch the dynamic tasks based on user input
                tasks = create_study_tasks(topic_input)
                
                # 2. Assemble the Crew
                study_crew = Crew(
                    agents=[professor, visualizer, quizmaster],
                    tasks=tasks,
                    verbose=True
                )
                
                # 3. Execute the workflow
                result = study_crew.kickoff()
                
                # 4. Display the results
                st.success("Study Guide Generated Successfully!")
                st.markdown("---")
                
                # Depending on the CrewAI version, the output format varies slightly.
                # .raw is the standard for newer versions.
                if hasattr(result, 'raw'):
                    st.markdown(result.raw)
                else:
                    st.markdown(result)
                    
            except Exception as e:
                st.error(f"An error occurred during generation: {str(e)}")