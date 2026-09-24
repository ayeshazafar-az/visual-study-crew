import os
from dotenv import load_dotenv
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import generate_concept_image

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

# 1. The Professor
professor = Agent(
    role="Senior Concept Analyst",
    goal="Analyze the input topic or document and break it down into clear, highly digestible explanations.",
    backstory="You are an award-winning university professor who excels at explaining complex subjects to beginners using analogies and structured breakdowns.",
    llm=llm,
    allow_delegation=False
)

# 2. The Visualizer
visualizer = Agent(
    role="Educational Mnemonic Designer",
    goal="Take educational concepts and create a highly descriptive prompt to generate a supporting visual aid.",
    backstory="You are a creative director for an education technology company. You know how to translate abstract text into stunning, memorable visuals that help students learn.",
    tools=[generate_concept_image],
    llm=llm,
    allow_delegation=False
)

# 3. The Quizmaster
quizmaster = Agent(
    role="Assessment Editor & Compiler",
    goal="Generate practice questions and synthesize the professor's explanation and the visualizer's image into a final formatted Markdown study guide.",
    backstory="You are a meticulous curriculum designer. You ensure study materials are engaging, test the user's knowledge, and are formatted perfectly in Markdown.",
    llm=llm,
    allow_delegation=False
)