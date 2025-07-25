# Reddit User Persona Generator

A Python script that automatically analyzes Reddit users' activity to create detailed UX personas. By scraping a user's posts and comments, then processing them with AI, it generates comprehensive profiles including interests, personality traits, behaviors, and demographics—complete with citations from their actual Reddit activity.

## Requirements

### 1. Reddit API Credentials

You need to create a Reddit app to obtain your credentials:

1. Open [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and log in.
2. Click **"create another app…"** at the bottom, select **script** under **Name:**
3. Fill in the app creation form:
    - **Name:** `colab-reddit-scraper` (or any name you like)
    - **Redirect URL:** `http://localhost:8080` (**must be exactly this**)

4. After creation, you'll get:
    - **client_id((personal use script)**: Under the app's name
    - **client_secret**: Next to "secret"

5. Pick a **user_agent** string like:
    ```
    data-scraper by u/youractualusername
    ```
    (Replace `youractualusername` with your Reddit username.)

### 2. OpenRouter API Key

You will need an OpenRouter or [OpenAI API key](https://openrouter.ai/settings/keys) for language model access.

### 3. Environment Variables

Store your credentials as environment variables (do **not** hardcode in your scripts):

| Variable Name         | Example Value                           | Description                         |
|---------------------- |-----------------------------------------|-------------------------------------|
| `REDDIT_CLIENT_ID`    | `abc12DEFGHIJkl`                        | Reddit app client ID                |
| `REDDIT_CLIENT_SECRET`| `mno34PQRSTU56vwxyz`                    | Reddit app client secret            |
| `REDDIT_USER_AGENT`   | `data-scraper by u/youractualusername`  | Your chosen user agent string       |
| `OPENAI_API_KEY`      | `sk-XXXXXXXX`                           | Your OpenAI or OpenRouter API key   |

**Set these in your environment before running the script.**  

I used colab, in colab you can add secrets in navigation bar on left hand side and provide Notebook access
<br>
<br>
<img width="484" height="417" alt="Screenshot_2025-07-17_22-22-44" src="https://github.com/user-attachments/assets/666bd910-9fb8-4748-81b9-364039e4a0d9" />

### 4. Models From Open router
You can chose any of the free models
I used 
<br>
1. [anthropic/claude-3-haiku (paid)](https://openrouter.ai/anthropic/claude-3-haiku)
2. [deepseek/deepseek-r1:free (free)](https://openrouter.ai/deepseek/deepseek-r1:free)

### 5. Code

Copy python file from [code](Code/reddit_persona_builder_by_bhavesh_srivastava.py), install the libraries and run the code

Use this line for runnig test cases and changing url
```
if __name__ == "__main__":
    test_url = "https://www.reddit.com/user/kojied/" # Test case 1
    #test_url = "https://www.reddit.com/user/Hungry-Move-6603/" # Test case 2
    run_analysis(test_url)
```

