import speech_recognition as sr
from pymongo import MongoClient
from datetime import datetime

from transformers import pipeline

# Setup summarizer
recognizer = sr.Recognizer()
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Mongo connection
client = MongoClient("mongodb://mongodb:27017/")
db = client["speechdb"]
collection = db["transcriptions"]

# Speech-to-text
r = sr.Recognizer()
mic = sr.Microphone()

print("Say something...")

def transcribe_and_summarize():
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"[Transcribed] {text}")

        summary = summarizer(text, max_length=60, min_length=20, do_sample=False)[0]['summary_text']
        print(f"[Summary] {summary}")

        # Store to DB
        doc = {
            "timestamp": datetime.datetime.utcnow(),
            "transcript": text,
            "summary": summary
        }
        collection.insert_one(doc)
        print("✅ Stored in DB")

    except sr.UnknownValueError:
        print("😕 Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Could not request results from Google: {e}")

