"""This module handles speech recognition and logging for transcriptions."""

import os
from datetime import datetime, timezone
from pymongo import MongoClient
import speech_recognition as sr
from transformers import pipeline

recognizer = sr.Recognizer()
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)

client = MongoClient("mongodb+srv://cluster0.zfwsq7e.mongodb.net/")
db = client["speech2text"]
collection = db["transcriptions"]  # to be changed


def transcribe_and_summarize():
    """Transcribes audio and stores transcription and summary in MongoDB."""
    mic = sr.Microphone()
    try:
        with mic as source:
            print("Speak now...")
            audio = recognizer.listen(source)
    except sr.WaitTimeoutError as e:
        print(f"Failed to capture audio: {e}")
        return

    try:
        text = recognizer.recognize_google(audio)
        print(f"Transcribed: {text}")
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio.")
        return
    except sr.RequestError as e:
        print(f"Google API error: {e}")
        return

    try:
        summary = summarizer(text, max_length=20, min_length=10, do_sample=False)[0][
            "summary_text"
        ]
        print(f"Summary: {summary}")
    except (KeyError, ValueError) as e:
        print(f"Summarization failed: {e}")
        return

    try:
        doc = {
            "timestamp": datetime.now(timezone.utc),
            "transcript": text,
            "summary": summary,
        }
        collection.insert_one(doc)
        print("Stored in DB")
    except Exception as e:
        print(f"Failed to store in DB: {e}")


if __name__ == "__main__":
    print("Testing MongoDB connection...")
    print("Databases:", client.list_database_names())
    print("Collections:", db.list_collection_names())
    transcribe_and_summarize()
