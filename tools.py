import urllib.parse
import os
import base64
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

@tool("Generate Concept Image")
def generate_concept_image(prompt: str) -> str:
    """
    Generates an educational image based on a descriptive prompt.
    Returns the markdown-formatted image link which must be embedded in the final report.
    """
    graphviz_code = prompt.strip()
    # Safely extract block if LLM added conversational text
    if "```dot" in graphviz_code:
        graphviz_code = graphviz_code.split("```dot")[1].split("```")[0]
    elif "```graphviz" in graphviz_code:
        graphviz_code = graphviz_code.split("```graphviz")[1].split("```")[0]
    elif "```" in graphviz_code:
        graphviz_code = graphviz_code.split("```")[1].split("```")[0]
        
    graphviz_code = graphviz_code.strip()
    
    import urllib.parse
    encoded_chart = urllib.parse.quote(graphviz_code)
    image_url = f"https://quickchart.io/graphviz?graph={encoded_chart}"
    
    # Return the direct markdown embedding syntax
    return f"![Technical Diagram]({image_url})"

@tool("Analyze Educational Image")
def analyze_educational_image(image_path: str, context: str = "Explain the concepts shown in this educational image in detail.") -> str:
    """
    Analyzes an educational image and extracts topics, notes, or diagrams and returns a comprehensive explanation.
    Pass the absolute file path to the image as the image_path argument.
    """
    if not os.path.exists(image_path):
        import logging
        logging.error(f"Image not found at {image_path}")
        return f"Error: Image not found at {image_path}"
        
    print(f"\n[DEBUG] 🕵️‍♂️ Professor is actively scanning the image at: {image_path}...")
    try:
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode("utf-8")
            
        # Get the GEMINI API KEY from env since we loaded it in app.py
        api_key = os.environ.get("GEMINI_API_KEY", "").replace('"', '').replace("'", "").strip()
        
        # Instantiate the model with vision capabilities
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        
        # Build the message payload
        message = HumanMessage(
            content=[
                {"type": "text", "text": context},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                }
            ]
        )
        
        # Invoke the model
        response = llm.invoke([message])
        return response.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"