import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import generate_concept_image, analyze_educational_image

# Force reload from .env, overriding any cached terminal variables
load_dotenv(override=True)

# Fetch and clean the API key
raw_key = os.environ.get("GEMINI_API_KEY", "")
cleaned_key = raw_key.replace('"', '').replace("'", "").strip()

# Initialize the LLM using the current active model
gemini_llm = LLM(
    model="gemini/gemini-3.5-flash-lite", 
    api_key=cleaned_key
)

# Fallback LLM to be dynamically swapped during high-demand 503 errors
gemini_fallback_llm = LLM(
    model="gemini/gemini-2.5-pro",
    api_key=cleaned_key
)

# 1. The Professor
professor = Agent(
    role="Senior Concept Analyst",
    goal="Analyze the input topic, document, or image and break it down into clear, highly digestible explanations. Use your image analysis tool when provided with an image path.",
    backstory="You are an award-winning university professor who excels at explaining complex subjects to beginners using analogies and structured breakdowns. You can also analyze educational visual materials.",
    tools=[analyze_educational_image],
    llm=gemini_llm,
    allow_delegation=False
)

# 2. The Visualizer
visualizer = Agent(
    role="Mermaid.js Diagram Engineer",
    goal="Translate complex technical concepts into flawless, structurally sound Mermaid.js flowchart code.",
    backstory="""You are a senior data architect and Mermaid.js specialist. The user absolutely loathes AI-generated abstract art and desperately needs accurate, clean, block-oriented diagrams (like the user's provided Flowchart images). You specialize in taking educational summaries and creating gorgeous text-labeled flowcharts strictly by writing native Mermaid.js syntax.""",
    tools=[generate_concept_image],
    allow_delegation=False,
    llm=gemini_llm
)

# 3. The Quizmaster
quizmaster = Agent(
    role="Assessment Editor & Compiler",
    goal="Generate practice questions and synthesize the professor's explanation and the visualizer's image into a final formatted Markdown study guide.",
    backstory="You are a meticulous curriculum designer. You ensure study materials are engaging, test the user's knowledge, and are formatted perfectly in Markdown.",
    llm=gemini_llm,
    allow_delegation=False
)