from openai import OpenAI
import os
from pdf import text
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Replace with your API key

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are an AI that extracts engineering tasks from documents and formats them as Linear tickets."},
        {"role": "user", "content": f"Extract engineering tasks from this document and generate structured tickets:\n{text}"}
    ]
)

# Print AI-generated tickets
print(response.choices[0].message.content)