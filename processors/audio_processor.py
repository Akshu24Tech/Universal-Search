"""
Universal Search — Audio Processor
Transcribes audio files using the Gemini API.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)

SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma"}

TRANSCRIPTION_PROMPT = """Transcribe this audio completely and accurately.
Include timestamps approximately every 30 seconds in the format [MM:SS].
Preserve speaker distinctions if multiple speakers are present.
Format the output as clean text with timestamp markers."""


class AudioProcessor:
    """Transcribe audio files via Gemini API."""

    def __init__(self):
        self.supported_extensions = SUPPORTED_AUDIO_EXTENSIONS

    def process(
        self,
        file_path: str = None,
        file_bytes: bytes = None,
        filename: str = "audio.mp3",
        mime_type: str = None,
    ) -> Dict[str, Any]:
        """
        Process an audio file and transcribe it.

        Returns: {
            "text": str (full transcript),
            "segments": [{time_start, time_end, text}],
            "metadata": {filename, type, duration_estimate}
        }
        """
        try:
            # Determine MIME type
            if mime_type is None:
                mime_type = self._get_mime_type(filename)

            # Upload file to Gemini
            if file_path and os.path.exists(file_path):
                logger.info(f"Uploading audio file: {filename}")
                uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
            elif file_bytes:
                # Save temp file for upload
                import tempfile

                ext = os.path.splitext(filename)[1] or ".mp3"
                with tempfile.NamedTemporaryFile(
                    suffix=ext, delete=False
                ) as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name
                logger.info(f"Uploading audio from bytes: {filename}")
                uploaded_file = genai.upload_file(tmp_path, mime_type=mime_type)
                os.unlink(tmp_path)
            else:
                raise ValueError("Either file_path or file_bytes must be provided")

            # Wait for file to be processed
            self._wait_for_file(uploaded_file)

            # Transcribe with Gemini
            logger.info(f"Transcribing audio: {filename}")
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(
                [uploaded_file, TRANSCRIPTION_PROMPT]
            )

            transcript = response.text
            segments = self._parse_segments(transcript)

            # Clean up uploaded file
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass

            result = {
                "text": transcript,
                "segments": segments,
                "metadata": {
                    "source": filename,
                    "type": "audio",
                    "total_chars": len(transcript),
                    "segment_count": len(segments),
                },
            }

            logger.info(
                f"Audio processed: {filename} | "
                f"{len(transcript)} chars, {len(segments)} segments"
            )
            return result

        except Exception as e:
            logger.error(f"Audio processing failed for {filename}: {e}")
            raise

    def _wait_for_file(self, uploaded_file, timeout: int = 120):
        """Wait for an uploaded file to finish processing."""
        start = time.time()
        while uploaded_file.state.name == "PROCESSING":
            if time.time() - start > timeout:
                raise TimeoutError(
                    f"File processing timed out after {timeout}s"
                )
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise RuntimeError(f"File processing failed: {uploaded_file.state.name}")

    def _parse_segments(self, transcript: str) -> List[Dict[str, Any]]:
        """Parse timestamped transcript into segments."""
        import re

        segments = []
        # Match patterns like [00:00] or [01:30]
        pattern = r"\[(\d{1,2}:\d{2})\]"
        parts = re.split(pattern, transcript)

        if len(parts) < 3:
            # No timestamps found — return whole transcript as one segment
            return [
                {
                    "time_start": "00:00",
                    "time_end": "end",
                    "text": transcript.strip(),
                }
            ]

        # parts: [text_before, timestamp1, text1, timestamp2, text2, ...]
        for i in range(1, len(parts) - 1, 2):
            time_start = parts[i]
            text = parts[i + 1].strip()
            # Next timestamp is the end time
            time_end = parts[i + 2] if i + 2 < len(parts) else "end"
            if text:
                segments.append(
                    {
                        "time_start": time_start,
                        "time_end": time_end if isinstance(time_end, str) and ":" in time_end else "end",
                        "text": text,
                    }
                )

        return segments if segments else [{"time_start": "00:00", "time_end": "end", "text": transcript.strip()}]

    @staticmethod
    def _get_mime_type(filename: str) -> str:
        """Determine MIME type from file extension."""
        ext = os.path.splitext(filename)[1].lower()
        mime_map = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".flac": "audio/flac",
            ".aac": "audio/aac",
            ".wma": "audio/x-ms-wma",
        }
        return mime_map.get(ext, "audio/mpeg")

    def get_segment_chunks(
        self, result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert processed audio into per-segment chunks."""
        chunks = []
        for seg in result["segments"]:
            if not seg["text"].strip():
                continue
            chunks.append(
                {
                    "content": seg["text"],
                    "images": [],
                    "metadata": {
                        "source": result["metadata"]["source"],
                        "type": "audio",
                        "time_start": seg["time_start"],
                        "time_end": seg["time_end"],
                    },
                }
            )
        return chunks
