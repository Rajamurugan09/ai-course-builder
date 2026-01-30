from typing import Optional
import requests
import os

from app.core.config import settings

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama2")  # Change to your preferred Ollama model


def generate_course_content(
    title: str,
    description: Optional[str] = None,
    prompt: Optional[str] = None
) -> str:
    """Generate course content using Ollama AI."""
    # Build the prompt
    if prompt:
        full_prompt = prompt
    else:
        full_prompt = f"Create a detailed course outline and content for a course titled '{title}'."
        if description:
            full_prompt += f" The course is about: {description}"
        full_prompt += "\n\nPlease provide:\n1. Course overview\n2. Learning objectives\n3. Detailed course outline with modules\n4. Key concepts and topics"
    
    try:
        # Call Ollama API with longer timeout (300 seconds = 5 minutes)
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Failed to generate content")
        else:
            return f"Error: Ollama API returned status code {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {str(e)}"
    except Exception as e:
        return f"Error generating content: {str(e)}"
