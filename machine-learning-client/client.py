"""This module pulls audio blobs from the 'audio' collection,
transcribes them, summarizes them, and writes results into 'messages'.
"""

from datetime import datetime, timezone
import io
from pymongo import MongoClient
import speech_recognition as sr
from transformers import pipeline

recognizer = sr.Recognizer()
summarizer = pipeline(
    "summarization", model="sshleifer/distilbart-cnn-12-6", device=-1
)

client = MongoClient("mongodb://mongodb:27017")
db = client["speech2text"]
audio_collection = db["recordings"]
messages_collection = db["messages"]

def process_audio():
    """Processes the latest unprocessed audio blob."""
    audio_doc = audio_collection.find_one(
        {"processed": {"$ne": True}}, sort=[("timestamp", -1)]
    )

    if not audio_doc:
        print("No new audio recordings found.")
        return

    audio_blob = audio_doc["data"]

    try:
        with sr.AudioFile(io.BytesIO(audio_blob)) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        print(f"[Transcribed] {text}")

        summary = summarizer(
            text, max_length=20, min_length=10, do_sample=False
        )[0]["summary_text"]
        print(f"Summary: {summary}")

    except (KeyError, ValueError) as e:
        print(f"Summarization failed: {e}")
        return
    except sr.UnknownValueError:
        print("Could not understand audio")
        return
    except sr.RequestError as e:
        print(f"Google Speech API error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    result_doc = {
        "timestamp": datetime.now(timezone.utc),
        "transcript": text,
        "summary": summary,
        "source_audio_id": audio_doc["_id"],
    }

    messages_collection.insert_one(result_doc)
    audio_collection.update_one(
        {"_id": audio_doc["_id"]}, {"$set": {"processed": True}}
    )
    print("Latest audio processed and stored.")


if __name__ == "__main__":
    process_audio()
    