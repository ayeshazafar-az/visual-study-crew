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
    model="gemini/gemini-pro",
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
    role="Educational Mnemonic Designer",
    goal="Take educational concepts and create a highly descriptive prompt to generate a supporting visual aid.",
    backstory="You are a creative director for an education technology company. You know how to translate abstract text into stunning, memorable visuals that help students learn.",
    tools=[generate_concept_image],
    llm=gemini_llm,
    allow_delegation=False
)

# 3. The Quizmaster
quizmaster = Agent(
    role="Assessment Editor & Compiler",
    goal="Generate practice questions and synthesize the professor's explanation and the visualizer's image into a final formatted Markdown study guide.",
    backstory="You are a meticulous curriculum designer. You ensure study materials are engaging, test the user's knowledge, and are formatted perfectly in Markdown.",
    llm=gemini_llm,
    allow_delegation=False
)