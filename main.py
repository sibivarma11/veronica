import requests
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS
import pygame
import time
import os
# ----------------------------
# CONFIG
# ----------------------------

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ----------------------------
# FETCH NEWS LOGIC
# ----------------------------

def fetch_space_news(endpoint):
    base_url = "https://api.spaceflightnewsapi.net/v4/"
    try:
        response = requests.get(base_url + endpoint)
        response.raise_for_status()
        results = response.json().get("results", [])
        # Space API uses 'summary'
        return [{"title": r["title"], "summary": r["summary"]} for r in results]
    except Exception as e:
        print(f"Space News Error: {e}")
        return []

def fetch_world_news(category=None, query=None):
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        print("\n[!] ERROR: NEWS_API_KEY not found in .env file.")
        print("Get a FREE key at: https://newsapi.org/register")
        return []
    
    base_url = "https://newsapi.org/v2/"
    if query:
        url = f"{base_url}everything?q={query}&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    else:
        cat_param = f"&category={category}" if category else ""
        url = f"{base_url}top-headlines?country=us{cat_param}&pageSize=5&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        # World News API uses 'description' as summary
        return [{"title": a["title"], "summary": a.get("description") or "No summary available."} for a in articles]
    except Exception as e:
        print(f"World News Error: {e}")
        return []

def get_user_selection():
    print("\n" + "="*45)
    print("      VERONICA NEWS AGENT v2.0")
    print("="*45)
    print(" [SPACE NEWS]")
    print("  1. General Articles     2. Blogs")
    print("  3. ISS & Reports        4. NASA News")
    print("  5. SpaceX News")
    print(" -------------------------------------------")
    print(" [WORLD NEWS] - Requires NewsAPI.org Key")
    print("  6. Top Headlines        7. Business")
    print("  8. Technology           9. Sports")
    print("  10. Health")
    print(" -------------------------------------------")
    print(" [SEARCH & SPECIAL]")
    print("  11. Search Global News  12. Search Space News")
    print("  13. Cyber Security News")
    
    choice = input("\nSelect an option (1-13): ").strip()
    
    if choice == "1": return "Space", fetch_space_news("articles")
    if choice == "2": return "Space Blogs", fetch_space_news("blogs")
    if choice == "3": return "Space Reports", fetch_space_news("reports")
    if choice == "4": return "NASA", fetch_space_news("articles?news_site=NASA")
    if choice == "5": return "SpaceX", fetch_space_news("articles?news_site=SpaceX")
    
    if choice == "6": return "World Headlines", fetch_world_news()
    if choice == "7": return "Business News", fetch_world_news(category="business")
    if choice == "8": return "Tech News", fetch_world_news(category="technology")
    if choice == "9": return "Sports News", fetch_world_news(category="sports")
    if choice == "10": return "Health News", fetch_world_news(category="health")
    if choice == "13": return "Cyber Security", fetch_world_news(query="cyber security")
    
    if choice == "11":
        q = input("Search Global News for: ").strip()
        return f"World Search: {q}", fetch_world_news(query=q)
    if choice == "12":
        q = input("Search Space News for: ").strip()
        return f"Space Search: {q}", fetch_space_news(f"articles?search={q}")
    
    print("\nInvalid choice. Defaulting to Space Articles.")
    return "Space", fetch_space_news("articles")

# ----------------------------
# MAIN EXECUTION
# ----------------------------

source_name, news_data = get_user_selection()

if not news_data:
    print("\nNo news found. Check your API keys or search terms.")
    exit()

news_text = ""
for idx, item in enumerate(news_data[:5], start=1):
    title = item.get("title", "No Title")
    summary = item.get("summary", "No Summary Available")
    news_text += f"News {idx}\nTitle: {title}\nSummary: {summary}\n\n"

print(f"\n===== FETCHED {source_name.upper()} NEWS =====\n")
print(news_text)

# ----------------------------
# GROQ AI SUMMARY
# ----------------------------

client = Groq(api_key=GROQ_API_KEY)

prompt = f"""
You are Veronica, a smart voice assistant. 
Summarize these {source_name} news items into a single, cohesive morning briefing.
Keep it natural, engaging, and professional. 
The summary should be under 200 words and optimized for being read aloud.

News Content:
{news_text}
"""

chat_completion = client.chat.completions.create(
    messages=[{"role": "user", "content": prompt}],
    model="llama-3.3-70b-versatile",
)

summary = chat_completion.choices[0].message.content

print("\n===== AI SUMMARY =====\n")
print(summary)

# ----------------------------
# TEXT TO SPEECH
# ----------------------------

tts = gTTS(text=summary, lang="en")
audio_file = "news.mp3"
tts.save(audio_file)

print("\nSpeaking News...\n")

# ----------------------------
# PLAY AUDIO
# ----------------------------

pygame.mixer.init()
pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    time.sleep(1)