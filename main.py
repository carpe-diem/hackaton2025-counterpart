from openai import OpenAI
import os
from pdf import text
from dotenv import load_dotenv
from linear_integration import create_tickets

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an AI that extracts engineering tasks from documents and formats them as Linear tickets."},
        {"role": "user", "content": f"Extract engineering tasks from this document and generate structured tickets:\n{text}"}
    ]
)

# Get AI-generated tickets
tickets_content = response.choices[0].message.content

print(tickets_content)

# Create tickets in Linear
create_tickets(tickets_content)
