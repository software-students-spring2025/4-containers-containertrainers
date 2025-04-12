import pytest
from unittest.mock import MagicMock, patch
import speech_recognition as sr
import client


@patch("client.sr.Microphone")
@patch("client.recognizer.listen")
@patch("client.recognizer.recognize_google")
@patch("client.summarizer")
@patch("client.collection.insert_one")
def test_transcribe_and_summarize_success(
    mock_insert, mock_summarizer, mock_recognize, mock_listen, mock_microphone
):
    mock_recognize.return_value = "This is a test sentence."
    mock_summarizer.return_value = [{"summary_text": "A test summary."}]
    mock_listen.return_value = MagicMock()

    client.transcribe_and_summarize()

    mock_recognize.assert_called_once()
    mock_summarizer.assert_called_once()
    mock_insert.assert_called_once()


@patch("client.sr.Microphone")
@patch("client.recognizer.listen")
@patch("client.recognizer.recognize_google", side_effect=sr.UnknownValueError())
def test_transcribe_handles_unknown_value(mock_recognize, mock_listen, mock_microphone):
    with patch("builtins.print") as mock_print:
        client.transcribe_and_summarize()
        mock_print.assert_any_call("Speech Recognition could not understand the audio.")


@patch("client.sr.Microphone")
@patch("client.recognizer.listen")
@patch(
    "client.recognizer.recognize_google", side_effect=sr.RequestError("API unavailable")
)
def test_transcribe_handles_request_error(mock_recognize, mock_listen, mock_microphone):
    with patch("builtins.print") as mock_print:
        client.transcribe_and_summarize()
        mock_print.assert_any_call("Google API error: API unavailable")


@patch("client.summarizer", side_effect=Exception("Summarizer failure"))
@patch("client.recognizer.listen")
@patch("client.recognizer.recognize_google", return_value="audio text")
@patch("client.sr.Microphone")
@patch("client.collection.insert_one")
def test_summarizer_crash(
    mock_insert, mock_mic, mock_recognize, mock_listen, mock_summarizer
):
    mock_listen.return_value = MagicMock()
    with patch("builtins.print") as mock_print:
        client.transcribe_and_summarize()
        mock_print.assert_any_call("Summarization failed: Summarizer failure")


@patch("client.recognizer.listen", side_effect=Exception("Incorrect audio stream"))
@patch("client.sr.Microphone")
def test_audio_input_failure(mock_mic, mock_listen):
    with patch("builtins.print") as mock_print:
        client.transcribe_and_summarize()
        mock_print.assert_any_call("Failed to capture audio: Incorrect audio stream")


@patch("client.summarizer")
@patch("client.sr.Microphone")
@patch("client.recognizer.listen")
@patch("client.recognizer.recognize_google")
@patch("client.collection.insert_one", side_effect=Exception("DB down"))
def test_database_failure_handled(
    mock_insert, mock_recognize, mock_listen, mock_mic, mock_summarizer
):
    mock_recognize.return_value = "text"
    mock_summarizer.return_value = [{"summary_text": "summary of audio"}]
    mock_listen.return_value = MagicMock()

    with patch("builtins.print") as mock_print:
        client.transcribe_and_summarize()
        mock_print.assert_any_call("Failed to store in DB")
