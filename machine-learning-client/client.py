"""This module handles speech recognition and logging for transcriptions."""

from datetime import datetime, timezone
from pymongo import MongoClient
import speech_recognition as sr
from transformers import pipeline

recognizer = sr.Recognizer()
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)

client = MongoClient("mongodb+srv://cluster0.zfwsq7e.mongodb.net/")
db = client["speech2text"]
collection = db["transcriptions"]  # to be changed

mic = sr.Microphone()

print("Say something...")


def transcribe_and_summarize():
    """Transcribes audio from the given file path using SpeechRecognition."""
    with mic as source:
        print("🎤 Speak now...")
        audio = recognizer.listen(source)
        # send audio to audio collection?

    try:
        text = recognizer.recognize_google(audio)
        print(f"[Transcribed] {text}")

        summary = summarizer(text, max_length=20, min_length=10, do_sample=False)[0][
            "summary_text"
        ]
        print(f"[Summary] {summary}")

        doc = {
            "timestamp": datetime.now(timezone.utc),
            "transcript": text,
            "summary": summary,
        }
        collection.insert_one(doc)
        print("✅ Stored in DB")

    except sr.UnknownValueError:
        print("😕 Could not understand audio")
    except sr.RequestError as e:
        print(f"❌ Could not request results from Google: {e}")


if __name__ == "__main__":
    transcribe_and_summarize()
