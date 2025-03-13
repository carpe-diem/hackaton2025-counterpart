import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
LINEAR_TEAM_ID = os.getenv("LINEAR_TEAM_ID")

def create_tickets(tickets_content):
    """
    Parse the AI-generated content and create tickets in Linear.

    Args:
        tickets_content (str): The AI-generated content containing ticket information
    """
    if not LINEAR_API_KEY:
        print("Error: LINEAR_API_KEY not found in environment variables")
        return

    if not LINEAR_TEAM_ID:
        print("Error: LINEAR_TEAM_ID not found in environment variables")
        return

    tickets = parse_tickets(tickets_content)
    successful_tickets = 0

    for ticket in tickets:
        success = create_linear_ticket(ticket)
        if success:
            successful_tickets += 1

    print(f"Successfully created {successful_tickets} out of {len(tickets)} tickets in Linear")

def parse_tickets(content):
    """
    Parse the AI-generated content to extract ticket information.

    Args:
        content (str): The AI-generated content

    Returns:
        list: A list of dictionaries containing ticket information
    """
    print("AI-generated content:")
    print(content)
    print("-" * 50)

    tickets = []

    # Try different parsing strategies
    # TODO: define output in prompt to make this more reliable

    # Strategy 1: Look for markdown-style tickets (# Title followed by content)
    if "# " in content:
        sections = content.split("# ")
        for section in sections[1:]:  # Skip the first empty section
            lines = section.strip().split("\n")
            if not lines:
                continue

            title = lines[0].strip()
            description = "\n".join(lines[1:]).strip()

            # Extract priority if mentioned in description
            priority = "medium"
            priority_keywords = {
                "urgent": ["urgent", "critical", "highest"],
                "high": ["high", "important"],
                "medium": ["medium", "normal"],
                "low": ["low", "minor"]
            }

            for level, keywords in priority_keywords.items():
                if any(keyword in description.lower() for keyword in keywords):
                    priority = level
                    break

            tickets.append({
                "title": title,
                "description": description,
                "priority": priority
            })

    # Strategy 2: Look for numbered tickets (1. Title)
    elif any(line.strip().startswith(f"{i}.") for i in range(1, 10) for line in content.split("\n")):
        current_ticket = None

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Check if this is a new ticket
            if any(line.startswith(f"{i}.") for i in range(1, 10)):
                # Save previous ticket if exists
                if current_ticket and current_ticket.get("title"):
                    tickets.append(current_ticket)

                # Start new ticket
                title = line.split(".", 1)[1].strip()
                current_ticket = {
                    "title": title,
                    "description": "",
                    "priority": "medium"
                }
            elif current_ticket:
                # Add to description of current ticket
                current_ticket["description"] += line + "\n"

                # Check for priority indicators
                if "priority" in line.lower():
                    if "high" in line.lower():
                        current_ticket["priority"] = "high"
                    elif "urgent" in line.lower() or "critical" in line.lower():
                        current_ticket["priority"] = "urgent"
                    elif "low" in line.lower():
                        current_ticket["priority"] = "low"

        # Add the last ticket
        if current_ticket and current_ticket.get("title"):
            tickets.append(current_ticket)

    # Strategy 3: Original approach - look for "Title:" prefixes
    else:
        ticket_blocks = [block.strip() for block in content.split("\n\n") if block.strip()]

        for block in ticket_blocks:
            lines = block.split("\n")

            title = ""
            description = ""
            priority = "medium"

            for line in lines:
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                elif line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Priority:"):
                    priority_text = line.replace("Priority:", "").strip().lower()
                    if priority_text in ["urgent", "high", "medium", "low"]:
                        priority = priority_text

            if title:
                tickets.append({
                    "title": title,
                    "description": description,
                    "priority": priority
                })

    # If no tickets were found, create a single ticket from the entire content
    if not tickets and content.strip():
        # Try to find a good title from the first line or first sentence
        lines = content.strip().split("\n")
        first_line = lines[0].strip()

        if len(first_line) > 10 and len(first_line) < 100:
            title = first_line
        else:
            # Use the first sentence or truncate if too long
            sentences = content.split(".")
            title = sentences[0].strip()
            if len(title) > 100:
                title = title[:97] + "..."

        tickets.append({
            "title": title,
            "description": content,
            "priority": "medium"
        })

    print(f"Parsed {len(tickets)} tickets:")
    for i, ticket in enumerate(tickets):
        print(f"Ticket {i+1}: {ticket['title']}")

    return tickets

def create_linear_ticket(ticket_data):
    """
    Create a ticket in Linear using the Linear GraphQL API.

    Args:
        ticket_data (dict): Dictionary containing ticket information

    Returns:
        bool: True if ticket was created successfully, False otherwise
    """
    url = "https://api.linear.app/graphql"

    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json"
    }

    # Map priority to Linear's priority levels
    priority_map = {
        "urgent": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }

    priority_value = priority_map.get(ticket_data.get("priority", "medium"), 3)

    # GraphQL mutation to create an issue
    mutation = """
    mutation CreateIssue($title: String!, $description: String, $teamId: String!, $priority: Int) {
        issueCreate(input: {
            title: $title,
            description: $description,
            teamId: $teamId,
            priority: $priority
        }) {
            success
            issue {
                id
                title
                url
            }
        }
    }
    """

    variables = {
        "title": ticket_data["title"],
        "description": ticket_data.get("description", ""),
        "teamId": LINEAR_TEAM_ID,
        "priority": priority_value
    }

    payload = {
        "query": mutation,
        "variables": variables
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response status: {response.status_code}")

        try:
            response_data = response.json()

            if "errors" in response_data:
                print(f"API Error: {json.dumps(response_data['errors'], indent=2)}")
                print(f"Failed to create ticket: {ticket_data['title']}")
                return False

            if response.status_code == 200 and response_data.get("data", {}).get("issueCreate", {}).get("success"):
                issue = response_data["data"]["issueCreate"]["issue"]
                print(f"Created ticket: {issue['title']} (ID: {issue['id']}, URL: {issue['url']})")
                return True
            else:
                print(f"Failed to create ticket: {ticket_data['title']}")
                print(f"Response: {json.dumps(response_data, indent=2)}")
                return False

        except json.JSONDecodeError:
            print(f"Failed to parse response as JSON. Raw response: {response.text}")
            return False

    except Exception as e:
        print(f"Error creating ticket: {str(e)}")
        import traceback
        traceback.print_exc()
        return False