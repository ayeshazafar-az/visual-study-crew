# Multi-Agent Study Forge 🎓

**Multi-Agent Study Forge** is an AI-powered educational application that transforms raw topics, text, or documents into comprehensively structured, visually illustrated study guides. 

Instead of relying on a single AI model to perform all tasks, the system utilizes a **CrewAI** orchestrator to delegate specific objectives to a team of specialized agents, ensuring higher quality reasoning, formatting, and multimodal outputs.

## 🌟 Key Features
- **Text Prompting**: Enter any subject (e.g., "The Architecture of a CPU") and let the agents break it down.
- **Document Ingestion**: Upload a PDF document for the agents to analyze and summarize into a study guide.
- **Multimodal Vision Integration**: Upload diagrams or visual notes (`png`, `jpg`); the agents use Gemini's deep vision capabilities to "read" the visual content and synthesize explanations.
- **Automated Tool Calling**: Agents seamlessly use custom tools (such as Pollinations.ai for generating concept art and Gemini Vision for diagram analysis) autonomously.

## 🤖 The AI Crew
The core logic relies on three distinct AI agents running sequentially:
1. **👨‍🏫 The Professor (Senior Concept Analyst)**: Ingests raw text or images and breaks down complex subjects into highly digestible, beginner-friendly explanations using analogies.
2. **🎨 The Visualizer (Educational Mnemonic Designer)**: Translates textbook concepts into abstract visualization prompts and interfaces with Pollinations API to generate a concrete visual aid.
3. **📝 The Quizmaster (Assessment Editor & Compiler)**: Synthesizes the text and image, generates a practice multiple-choice quiz, and compiles the final polished Markdown document.

## 🛠️ Tech Stack
- **Python 3**
- **Streamlit** (UI Framework)
- **CrewAI** (Agent Orchestrator)
- **Google Gemini API** (LLM & Vision Models via Langchain SDK)
- **PyPDF2** (Document Parsing)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayeshazafar-az/visual-study-crew.git
   cd visual-study-crew
   ```

2. **Install dependencies:**
   Make sure you have python installed. It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup:**
   Create a `.env` file in the root of your project and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY="your-gemini-api-key-here"
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   The UI will launch in your default web browser!

## 📝 License
This project is for educational purposes. Feel free to fork and build upon it!
