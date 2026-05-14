import requests
from groq import Groq
from gtts import gTTS
import pygame
import time

# ----------------------------
# CONFIG
# ----------------------------

GROQ_API_KEY = "REDACTED"


# ----------------------------
# FETCH NEWS
# ----------------------------

url = "https://api.spaceflightnewsapi.net/v4/articles/"

response = requests.get(url)
data = response.json()

articles = data.get("results", [])

news_text = ""

for idx, article in enumerate(articles[:5], start=1):
    title = article.get("title", "")
    summary = article.get("summary", "")

    news_text += f"""
News {idx}
Title: {title}
Summary: {summary}

"""

print("\n===== FETCHED NEWS =====\n")
print(news_text)

# ----------------------------
# GROQ AI SUMMARY
# ----------------------------

client = Groq(api_key=GROQ_API_KEY)

prompt = f"""
Summarize these latest news articles
in simple spoken English.

Keep it short and natural like a voice assistant.

{news_text}
"""

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
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