"""Unit tests for the client module that handles transcription and summarization."""

import io
from unittest.mock import patch, MagicMock
import client


@patch("client.audio_collection.find_one")
@patch("client.messages_collection.insert_one")
@patch("client.audio_collection.update_one")
@patch("client.summarizer")
@patch("client.recognizer.recognize_google", return_value="test audio")
@patch("client.recognizer.record")
@patch("client.sr.AudioFile")
def test_process_audio_success(
    mock_audiofile,
    mock_record,
    mock_recognize,
    mock_summarizer,
    mock_update,
    mock_insert,
    mock_find,
):
    """Test the full successful audio processing flow."""
    mock_find.return_value = {"_id": "abc123", "data": b"fakeblob"}
    mock_audiofile.return_value.__enter__.return_value = MagicMock()
    mock_summarizer.return_value = [{"summary_text": "short summary"}]

    with patch("builtins.print") as mock_print:
        client.process_audio()

        mock_find.assert_called_once()
        mock_recognize.assert_called_once()
        mock_summarizer.assert_called_once()
        mock_insert.assert_called_once()
        mock_update.assert_called_once()
        mock_print.assert_any_call("Summary: short summary")
        mock_print.assert_any_call("Latest audio processed and stored.")


@patch("client.audio_collection.find_one", return_value=None)
def test_no_audio_found(mock_find):
    """Test when no audio documents exist."""
    with patch("builtins.print") as mock_print:
        client.process_audio()
        mock_print.assert_any_call("No new audio recordings found.")
        mock_find.assert_called_once()


@patch("client.audio_collection.find_one", return_value={"_id": "x", "data": b"invalid"})
@patch("client.sr.AudioFile", side_effect=Exception("corrupted audio"))
def test_audiofile_crash(mock_audiofile, mock_find):
    """Test when loading audio fails."""
    with patch("builtins.print") as mock_print:
        client.process_audio()
        mock_audiofile.assert_called_once()
        mock_print.assert_any_call("Unexpected error: corrupted audio")


@patch("client.audio_collection.find_one", return_value={"_id": "x", "data": b"blob"})
@patch("client.recognizer.recognize_google", side_effect=Exception("fail"))
@patch("client.sr.AudioFile")
@patch("client.recognizer.record", return_value="mock_audio")
def test_recognition_crash(mock_record, mock_audiofile, mock_recognize, mock_find):
    """Test handling of failure in speech recognition."""
    mock_audiofile.return_value.__enter__.return_value = MagicMock()
    with patch("builtins.print") as mock_print:
        client.process_audio()
        mock_recognize.assert_called_once()
        mock_print.assert_any_call("Unexpected error: fail")


@patch("client.audio_collection.find_one", return_value={"_id": "x", "data": b"blob"})
@patch("client.recognizer.recognize_google", return_value="sample text")
@patch("client.summarizer", side_effect=Exception("summary error"))
@patch("client.sr.AudioFile")
@patch("client.recognizer.record", return_value="mock_audio")
def test_summary_crash(mock_record, mock_audiofile, mock_summarizer, mock_recognize, mock_find):
    """Test if summarization failure is caught"""
    mock_audiofile.return_value.__enter__.return_value = MagicMock()
    with patch("builtins.print") as mock_print:
        client.process_audio()
        mock_summarizer.assert_called_once()
        mock_print.assert_any_call("Unexpected error: summary error")
