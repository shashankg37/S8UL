import os
from groq import Groq


def web_search(query: str) -> str:
    """Searches the live web for current information."""

    try:
        client = Groq(
            api_key=os.environ["GROQ_API_KEY"],
            default_headers={
                "Groq-Model-Version": "latest"
            }
        )

        response = client.chat.completions.create(
            model="groq/compound-mini",
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Web search failed: {e}"