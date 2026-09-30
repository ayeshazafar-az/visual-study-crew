# Multi-Agent Study Forge 🎓✨

**Multi-Agent Study Forge** is an AI-powered educational dashboard that transforms raw topics, textbook snippets, and uploaded images into comprehensively structured, visually illustrated study guides. 

By bypassing traditional single-model constraints, this application deploys a **CrewAI Hierarchical Orchestrator** to delegate objectives across a team of specialized agents, guaranteeing superior logical reasoning, strictly formatted layouts, and multimodal precision.

## 🌟 Core Features

- **Multi-Session Conversational Dashboard**: A persistent, ChatGPT-style chat interface featuring a dynamic sidebar that automatically localizes and tracks your parallel chat sessions *without* needing cloud accounts or database logins.
- **Ephemeral Session Security**: History is securely tethered to your browser's active `st.session_state`. When you terminate the browser tab, the memory is strictly wiped—guaranteeing 100% private, serverless operation.
- **Full-Spread PDF Exporting**: Instantly download the entire conversational study session into a cleanly formatted Master PDF, or snapshot individual Quick Action responses.
- **Automated Graphviz DOT Layouts**: The multi-agent cluster autonomously designs complex structural architectures and formats them into strict block diagrams, auto-wrapped and rendered natively inside your chat.
- **High-Availability Engine Core**: Hardened against free-tier API congestion limits by strictly mapping the orchestration agents to the reliable legacy `gemini-3.1-flash-lite` cluster.

## 🤖 The AI Crew

1. **👨‍🏫 The Professor (Senior Concept Analyst)**: Ingests raw text, images, or PDFs to explain complex subjects in a structured, accessible manner.
2. **🎨 The Visualizer (Graphviz Architect)**: Translates textbook concepts into strict textual DOT architectures for block diagram generation.
3. **📝 The Quizmaster (Assessment Editor)**: Synthesizes material to generate challenging multiple-choice quizzes and interactive flashcards.

## 🛠️ Technology Stack
- **Python 3**
- **Streamlit** (Conversational UI & Serverless State Management)
- **CrewAI** (Agent Orchestrator)
- **Google Gemini API** (LLM & Vision Multimodal Models)
- **PyPDF2 & QuickChart API** (Parsing and Rendering)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayeshazafar-az/visual-study-crew.git
   cd visual-study-crew
   ```

2. **Install dependencies:**
   Make sure you have Python installed. It is strongly recommended to use a virtual environment (`venv`).
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
