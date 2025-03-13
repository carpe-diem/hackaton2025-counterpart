from openai import OpenAI
import os
from pdf import text
from dotenv import load_dotenv
from linear_integration import create_tickets  # Import the new module

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Replace with your API key

response = client.responses.create(
    model="gpt-4o",
    instructions="You are an AI that extracts engineering tasks from documents and formats them as Linear tickets.",
    input=f"Extract engineering tasks from this document and generate structured tickets:\n{text}",
)

print(response.output_text)
