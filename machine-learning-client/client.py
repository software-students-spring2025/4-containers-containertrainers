import speech_recognition as sr
from pymongo import MongoClient
from datetime import datetime, timezone
from transformers import pipeline

recognizer = sr.Recognizer()
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)

client = MongoClient("mongodb://mongodb:27017/") # to be changed
db = client["speechdb"]
collection = db["transcriptions"]

mic = sr.Microphone()

print("Say something...")

def transcribe_and_summarize():
    with mic as source:
        print("🎤 Speak now...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"[Transcribed] {text}")

        summary = summarizer(text, max_length=20, min_length=10, do_sample=False)[0]['summary_text']
        print(f"[Summary] {summary}")

        doc = {
            "timestamp": datetime.now(timezone.utc), 
            "transcript": text,
            "summary": summary
        }
        collection.insert_one(doc)
        print("✅ Stored in DB")

    except sr.UnknownValueError:
        print("😕 Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Could not request results from Google: {e}")

transcribe_and_summarize()
