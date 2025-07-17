# Install dependencies
!pip install -q asyncpraw openai python-dotenv nest_asyncio

import os
import re
import datetime
import asyncio
from google.colab import userdata, files
from openai import AsyncOpenAI
import asyncpraw
import nest_asyncio

# Apply nest_asyncio to work in Colab
nest_asyncio.apply()


class Config:
    MAX_COMMENTS = 100  # Values can be changed for better persona building
    MAX_POSTS = 30
    MODEL = "deepseek/deepseek-r1:free"  # Recommended free model
    PERSONA_TOKENS = 10000
    TEMPERATURE = 0.5

# Clients
class Clients:
    def __init__(self):
        self.reddit = None
        self.openai = None

    async def initialize(self):
        try:
            # Initialize Reddit client
            self.reddit = asyncpraw.Reddit(
                client_id=userdata.get("REDDIT_CLIENT_ID"),
                client_secret=userdata.get("REDDIT_CLIENT_SECRET"),
                user_agent=userdata.get("REDDIT_USER_AGENT"),
            )
            print("Reddit client ready")

            # Initialize OpenAI client for OpenRouter
            self.openai = AsyncOpenAI(
                api_key=userdata.get("OPENAI_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            print(f"OpenRouter ready (using {Config.MODEL})")

        except Exception as e:
            print(f"Failed to initialize clients: {e}")
            await self.close()
            raise

    async def close(self):
        if self.reddit:
            await self.reddit.close()
        if hasattr(self.openai, 'close'):
            await self.openai.close()

# Prompt for the LLM
SYSTEM_PROMPT = """You are a professional UX researcher creating detailed user personas based on Reddit activity. Structure your analysis exactly like this template:

[USERNAME]
[AGE] [OCCUPATION] [STATUS] [LOCATION] [ARCHETYPE]

---

[KEY TRAIT 1] [KEY TRAIT 2]

### [SUBTRAIT 1] [SUBTRAIT 2]

---

## MOTIVATIONS

- [MOTIVATION 1] [MOTIVATION 2] [MOTIVATION 3]
- [PERSONALITY TRAITS]

---

## BEHAVIOR & HABITS

- [OBSERVATION 1] ([c#] or [s#])
- [OBSERVATION 2] ([c#] or [s#])
- [OBSERVATION 3] ([c#] or [s#])

---

## GOALS & NEEDS

- [GOAL 1]
- [GOAL 2]
- [GOAL 3]

---

## FRUSTRATIONS

- [FRUSTRATION 1]
- [FRUSTRATION 2]
- [FRUSTRATION 3]

---

"Direct quote summarizing their perspective" ([c#] or [s#])

ANALYSIS GUIDELINES:
1. Infer demographics from context clues in posts/comments
2. Identify archetypes like: The Creator, The Caregiver, The Explorer, etc.
3. For motivations/needs/frustrations, focus on practical, actionable insights
4. Include both observed behaviors and inferred psychological traits
5. Always cite specific comments/posts as evidence using [c#] or [s#]
6. Keep descriptions concise and professional

EXAMPLE OUTPUT:
**kojied**
31 Tech Professional Single New York, US The Creator

---

Analytical Curious

### Innovative Detail-Oriented

---

## MOTIVATIONS

- LEARNING COMMUNITY INNOVATION
- INTJ PERSONALITY: INTROVERTED INTUITIVE THINKING JUDGING

---

## BEHAVIOR & HABITS

- Regularly posts detailed game analyses ([s3], [s5], [s7])
- Engages in technical discussions about game mechanics ([c12], [c15])
- Shares personal gaming experiences with self-reflection ([c4], [c8])

---

## GOALS & NEEDS

- To find like-minded gaming enthusiasts
- To understand complex game systems
- To share specialized knowledge

---

## FRUSTRATIONS

- Overly simplistic game discussions ([c22])
- Lack of technical depth in reviews ([s9])
- Toxic behavior in gaming communities ([c17])

---

"I value deep, thoughtful discussions about game design more than quick reactions." ([s5])
"""

# Data Collection
async def fetch_user_content(clients, username):
    content = {"comments": [], "posts": []}
    try:
        print(f"\nFetching content for u/{username}...")
        redditor = await clients.reddit.redditor(username)  # Changed to use clients object

        # Get comments with progress tracking
        comments = []
        async for comment in redditor.comments.new(limit=Config.MAX_COMMENTS):  # Uses Config value
            comments.append(f"[c{len(comments)}] {comment.body}")  # Added index tags
            if len(comments) % 10 == 0:  # Progress feedback
                print(f"Fetched {len(comments)} comments...")

        # Get posts with progress tracking
        posts = []
        async for post in redditor.submissions.new(limit=Config.MAX_POSTS):
            text = f"{post.title}\n{post.selftext}" if post.selftext else post.title
            posts.append(f"[s{len(posts)}] {text}")  # Added index tags
            if len(posts) % 5 == 0:  # Progress feedback
                print(f"Fetched {len(posts)} posts...")

        print(f"Collected {len(comments)} comments and {len(posts)} posts")
        return {"comments": comments, "posts": posts}

    except Exception as e:
        print(f"Error fetching content: {e}")
        return content  # Returns empty dict on error

# Persona Generation
async def generate_persona(clients, username, content):
    if not content["comments"] and not content["posts"]:
        return "No content available to analyze."

    # Prepare input for LLM
    user_content = (
        f"Analyze u/{username} based on these activities:\n\n"
        "COMMENTS:\n" + "\n".join(content["comments"][:100]) + "\n\n"
        "POSTS:\n" + "\n".join(content["posts"][:30])
    )

    try:
        print("\nGenerating persona...")
        response = await clients.openai.chat.completions.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            max_tokens=Config.PERSONA_TOKENS,
            temperature=Config.TEMPERATURE
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"\n Generation error: {str(e)}")
        return f"Persona generation failed. Error: {str(e)}"

# Save Results
def save_results(username, persona):
    try:
        safe_name = re.sub(r"[^\w-]", "_", username)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"persona_{safe_name}_{timestamp}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            # Simple box design for the header
            f.write(f"╔{'═'*30}╗\n")
            f.write(f"║{'REDDIT PERSONA ANALYSIS'.center(30)}║\n")
            f.write(f"╠{'═'*30}╣\n")
            f.write(f"║ User: u/{username.ljust(22)}║\n")
            f.write(f"║ Generated: {timestamp.ljust(19)}║\n")
            f.write(f"╚{'═'*30}╝\n\n")
            f.write(persona)

        print(f"Saved to {filename}")
        return filename

    except Exception as e:
        print(f"Error saving results: {e}")
        return None

async def analyze_user(reddit_url):
    clients = Clients()
    output_file = None  # Initialize output_file

    try:
        # Validate URL
        if not reddit_url.startswith("https://www.reddit.com/user/"):
            raise ValueError("Invalid Reddit user URL format")

        username = reddit_url.split("/user/")[1].strip("/")
        if not username:
            raise ValueError("Couldn't extract username from URL")

        print(f"\nAnalyzing u/{username}...")

        # Initialize clients
        await clients.initialize()

        # Fetch content
        content = await fetch_user_content(clients, username)

        # Generate persona
        persona = await generate_persona(clients, username, content)

        # Save results
        output_file = save_results(username, persona)
        if output_file:  # Only try to download if file was saved successfully
            files.download(output_file)

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
    finally:
        await clients.close()
        return output_file  # Return filename even if None

def run_analysis(url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(analyze_user(url))
    finally:
        loop.close()

# Run this
if __name__ == "__main__":
    test_url = "https://www.reddit.com/user/kojied/" # Test case 1
    #test_url = "https://www.reddit.com/user/Hungry-Move-6603/" # Test case 2
    run_analysis(test_url)
