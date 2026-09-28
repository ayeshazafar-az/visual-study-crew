# Multi-Agent Study Forge 🎓

**Multi-Agent Study Forge** is an AI-powered educational application that transforms raw topics, text, or documents into comprehensively structured, visually illustrated study guides. 

Instead of relying on a single AI model to perform all tasks, the system utilizes a **CrewAI** orchestrator to delegate specific objectives to a team of specialized agents, ensuring higher quality reasoning, formatting, and multimodal outputs.

- **Conversational ChatGPT-Style Dashboard**: A persistent chat UI allowing you to ask follow-up questions and generate multiple study modules in a single session.
- **Ephemeral Session Security**: Chat memory securely resides in the browser state and is strictly wiped on refresh—ensuring private, footprint-free usage.
- **PDF Export Engines**: Export the entire holistic study session into a Master PDF, or download individual Quick Action responses as cleanly formatted, standalone PDF snapshots.
- **Automated Tool Calling & Graphviz Layouts**: The multi-agent cluster automatically formats responses, analyzes attachments, and outputs structured, complex block-diagram architecture layouts using QuickChart Graphviz rendering.

## 🤖 The AI Crew
The core logic relies on a Hierarchical Multi-Agent cluster, utilizing the Gemini 3.5 Flash and Gemini 3.1 Pro Preview models:
1. **👨‍🏫 The Professor (Senior Concept Analyst)**: Ingests raw text, images, or PDFs to explain complex subjects in a beginner-friendly manner.
2. **🎨 The Visualizer (Graphviz Architect)**: Translates textbook concepts into strict textual DOT architecture definitions for structural block diagram generation.
3. **📝 The Quizmaster (Assessment Editor)**: Synthesizes content and generates multiple-choice quizzes or flashcards based on the user's specific context.

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
