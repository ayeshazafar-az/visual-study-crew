import urllib.parse
from crewai.tools import tool

@tool("Generate Concept Image")
def generate_concept_image(prompt: str) -> str:
    """
    Generates an educational image based on a descriptive prompt.
    Returns the markdown-formatted image link which must be embedded in the final report.
    """
    # Encode the prompt to make it URL-safe
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Construct the Pollinations.ai URL
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"
    
    # Return the direct markdown embedding syntax
    return f"![Visual Aid]({image_url})"