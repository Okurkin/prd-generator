import os
import sys
from openai import OpenAI, RateLimitError

# Check for required environment variables
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("ERROR: OPENAI_API_KEY not found in environment variables!")
    print("Please set your OpenAI API key in the .env file")
    sys.exit(1)

client = OpenAI(api_key=openai_api_key)

def generate_prd_section(section_title: str, mrd_text: str, product_name: str) -> str:
    """Generate a specific section of PRD based on MRD content (legacy function)"""
    prompt = (
        f"You are a product manager generating a PRD. Based on the following MRD and product name '{product_name}', "
        f"write a concise and clear PRD section titled '{section_title}'. Avoid repetition and explain only the key ideas.\n\n"
        f"MRD Content:\n{mrd_text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o as GPT-5 is not yet available
            messages=[
                {"role": "system", "content": "You are a professional product document writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()

    except RateLimitError:
        return "Rate limit exceeded. Please try again later."
    except Exception as e:
        return f"Error: {str(e)}"

def generate_interactive_prd_update(current_prd: str, user_request: str, product_name: str, context: str = "") -> str:
    """Generate an updated PRD based on user request in interactive chat mode"""
    prompt = f"""
You are an expert product manager helping to iteratively improve a PRD document.

Current PRD for '{product_name}':
{current_prd}

Additional context:
{context}

User's request for changes:
{user_request}

Please provide an updated version of the PRD that incorporates the user's request. 
Keep the existing structure but modify/add/remove content as requested.
Be precise and professional in your modifications.
Return only the updated PRD content, no additional commentary.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional product document writer specializing in PRD creation and iterative improvements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        return "Rate limit exceeded. Please try again later."
    except Exception as e:
        return f"Error: {str(e)}"

def generate_initial_prd(mrd_content: str, product_name: str, additional_context: str = "") -> str:
    """Generate initial comprehensive PRD from MRD content"""
    prompt = f"""
Create a comprehensive Product Requirements Document (PRD) for '{product_name}' based on the following Market Requirements Document (MRD) content.

MRD Content:
{mrd_content}

Additional Context:
{additional_context}

Please structure the PRD with the following sections:
1. Executive Summary
2. Product Overview
3. User Stories & Requirements
4. Technical Requirements
5. Success Metrics
6. Timeline & Milestones
7. Risk Assessment

Make it comprehensive, clear, and actionable. Use proper markdown formatting.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional product manager creating detailed PRD documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        return "Rate limit exceeded. Please try again later."
    except Exception as e:
        return f"Error: {str(e)}"

def generate_change_summary(old_content: str, new_content: str) -> str:
    """Generate a summary of changes between two PRD versions"""
    prompt = f"""
Compare these two versions of a PRD and provide a brief summary of the key changes made:

Previous version:
{old_content[:1000]}...

New version:
{new_content[:1000]}...

Provide a concise summary of what was changed, added, or removed.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing document changes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Unable to generate change summary"
