"""
Universal Search — Video Processor
Extracts keyframes via OpenCV and transcribes audio via Gemini.
"""

import os
import io
import time
import tempfile
import logging
from typing import Dict, Any, List, Optional

import cv2
import numpy as np
from PIL import Image
import google.generativeai as genai

logger = logging.getLogger(__name__)

SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

KEYFRAME_DESCRIPTION_PROMPT = """Describe what is shown in this video frame in detail.
Focus on: visual content, text/slides visible, diagrams, people, and any educational content.
Be specific and concise (2-3 sentences max)."""


class VideoProcessor:
    """Extract keyframes and transcribe video files."""

    def __init__(self, keyframe_interval: int = 10, scene_threshold: float = 30.0):
        """
        Args:
            keyframe_interval: Extract a frame every N seconds
            scene_threshold: Frame difference threshold for scene change detection
        """
        self.keyframe_interval = keyframe_interval
        self.scene_threshold = scene_threshold
        self.supported_extensions = SUPPORTED_VIDEO_EXTENSIONS

    def process(
        self,
        file_path: str = None,
        file_bytes: bytes = None,
        filename: str = "video.mp4",
        mime_type: str = None,
    ) -> Dict[str, Any]:
        """
        Process a video file: extract keyframes + transcribe audio.

        Returns: {
            "text": str (combined transcript + descriptions),
            "keyframes": [{timestamp, image: PIL.Image, description: str}],
            "transcript": str,
            "metadata": {filename, type, duration, fps, frame_count}
        }
        """
        try:
            # Handle file bytes by writing to temp file
            tmp_path = None
            if file_bytes and not file_path:
                ext = os.path.splitext(filename)[1] or ".mp4"
                tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                tmp.write(file_bytes)
                tmp.close()
                file_path = tmp.name
                tmp_path = tmp.name

            if not file_path or not os.path.exists(file_path):
                raise ValueError("Valid file_path required for video processing")

            # Step 1: Extract keyframes with OpenCV
            logger.info(f"Extracting keyframes from: {filename}")
            keyframes = self._extract_keyframes(file_path)

            # Step 2: Get descriptions for each keyframe via Gemini
            logger.info(f"Describing {len(keyframes)} keyframes...")
            for kf in keyframes:
                try:
                    kf["description"] = self._describe_frame(kf["image"])
                except Exception as e:
                    logger.warning(f"Frame description failed at {kf['timestamp']}: {e}")
                    kf["description"] = "Frame description unavailable."
                time.sleep(0.5)  # Rate limiting

            # Step 3: Transcribe audio via Gemini
            logger.info(f"Transcribing video audio: {filename}")
            transcript = self._transcribe_audio(file_path, filename, mime_type)

            # Combine descriptions and transcript
            description_text = "\n\n".join(
                f"[{kf['timestamp']}] {kf['description']}" for kf in keyframes
            )
            full_text = f"TRANSCRIPT:\n{transcript}\n\nVISUAL DESCRIPTIONS:\n{description_text}"

            # Get video metadata
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            cap.release()

            # Clean up temp file
            if tmp_path:
                os.unlink(tmp_path)

            result = {
                "text": full_text,
                "keyframes": keyframes,
                "transcript": transcript,
                "metadata": {
                    "source": filename,
                    "type": "video",
                    "duration_seconds": round(duration, 1),
                    "duration_formatted": self._format_time(duration),
                    "fps": round(fps, 1),
                    "frame_count": frame_count,
                    "keyframe_count": len(keyframes),
                    "total_chars": len(full_text),
                },
            }

            logger.info(
                f"Video processed: {filename} | "
                f"{self._format_time(duration)}, {len(keyframes)} keyframes"
            )
            return result

        except Exception as e:
            logger.error(f"Video processing failed for {filename}: {e}")
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _extract_keyframes(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract keyframes using interval sampling + scene change detection."""
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {file_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval_frames = int(fps * self.keyframe_interval)

        keyframes = []
        prev_frame = None
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_time = frame_idx / fps
            is_interval = frame_idx % interval_frames == 0
            is_scene_change = False

            # Scene change detection
            if prev_frame is not None:
                diff = cv2.absdiff(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                    cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY),
                )
                mean_diff = np.mean(diff)
                is_scene_change = mean_diff > self.scene_threshold

            if is_interval or is_scene_change:
                # Convert BGR to RGB PIL Image
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)

                # Resize if too large (max 1024px on longest side)
                max_dim = max(pil_image.size)
                if max_dim > 1024:
                    scale = 1024 / max_dim
                    new_size = (
                        int(pil_image.width * scale),
                        int(pil_image.height * scale),
                    )
                    pil_image = pil_image.resize(new_size, Image.LANCZOS)

                keyframes.append(
                    {
                        "timestamp": self._format_time(current_time),
                        "time_seconds": round(current_time, 1),
                        "image": pil_image,
                        "frame_index": frame_idx,
                        "trigger": "interval" if is_interval else "scene_change",
                    }
                )

            prev_frame = frame.copy()
            frame_idx += 1

        cap.release()
        logger.info(f"Extracted {len(keyframes)} keyframes from {total_frames} total frames")
        return keyframes

    def _describe_frame(self, image: Image.Image) -> str:
        """Get a text description of a keyframe via Gemini."""
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            [KEYFRAME_DESCRIPTION_PROMPT, image]
        )
        return response.text.strip()

    def _transcribe_audio(
        self, file_path: str, filename: str, mime_type: str = None
    ) -> str:
        """Transcribe the audio track of a video via Gemini."""
        if mime_type is None:
            mime_type = self._get_mime_type(filename)

        try:
            uploaded_file = genai.upload_file(file_path, mime_type=mime_type)

            # Wait for processing
            start = time.time()
            while uploaded_file.state.name == "PROCESSING":
                if time.time() - start > 300:
                    raise TimeoutError("Video upload processing timed out")
                time.sleep(3)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name == "FAILED":
                raise RuntimeError("Video upload processing failed")

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(
                [
                    uploaded_file,
                    "Transcribe all spoken content in this video completely. "
                    "Include timestamps every 30 seconds in [MM:SS] format.",
                ]
            )

            # Clean up
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass

            return response.text.strip()

        except Exception as e:
            logger.warning(f"Audio transcription failed, continuing without: {e}")
            return "Audio transcription unavailable."

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds into MM:SS string."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    @staticmethod
    def _get_mime_type(filename: str) -> str:
        """Determine MIME type from file extension."""
        ext = os.path.splitext(filename)[1].lower()
        mime_map = {
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".mkv": "video/x-matroska",
            ".webm": "video/webm",
        }
        return mime_map.get(ext, "video/mp4")

    def get_video_chunks(
        self, result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert processed video into chunks (keyframes + transcript segments)."""
        chunks = []

        # Keyframe chunks (with images for interleaved embedding)
        for kf in result["keyframes"]:
            chunks.append(
                {
                    "content": kf["description"],
                    "images": [kf["image"]],
                    "metadata": {
                        "source": result["metadata"]["source"],
                        "type": "video",
                        "timestamp": kf["timestamp"],
                        "has_keyframe": True,
                    },
                }
            )

        # Transcript chunk
        if result["transcript"] and result["transcript"] != "Audio transcription unavailable.":
            chunks.append(
                {
                    "content": result["transcript"],
                    "images": [],
                    "metadata": {
                        "source": result["metadata"]["source"],
                        "type": "video",
                        "timestamp": "00:00",
                        "has_keyframe": False,
                    },
                }
            )

        return chunks
