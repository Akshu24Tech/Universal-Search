"""
Universal Search — PDF Processor
Extracts text and images from PDF files using PyMuPDF.
"""

import io
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

logger = logging.getLogger(__name__)

# Minimum image size to extract (skip tiny icons/artifacts)
MIN_IMAGE_SIZE = (50, 50)
# Supported image formats for extraction
SUPPORTED_IMAGE_FORMATS = {"png", "jpeg", "jpg", "bmp", "tiff"}


class PDFProcessor:
    """Extract text and images from PDF documents."""

    def __init__(self):
        self.supported_extensions = {".pdf"}

    def process(
        self,
        file_path: str = None,
        file_bytes: bytes = None,
        filename: str = "document.pdf",
    ) -> Dict[str, Any]:
        """
        Process a PDF file and extract text + images.

        Returns: {
            "text": str (full extracted text),
            "pages": [{page_num, text, images: [PIL.Image]}],
            "metadata": {filename, total_pages, total_chars, has_images},
            "images": [PIL.Image] (all extracted images)
        }
        """
        try:
            if file_bytes:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
            elif file_path:
                doc = fitz.open(file_path)
            else:
                raise ValueError("Either file_path or file_bytes must be provided")

            pages_data = []
            all_text_parts = []
            all_images = []

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Extract text
                page_text = page.get_text("text")
                all_text_parts.append(page_text)

                # Extract images
                page_images = self._extract_page_images(page, doc)
                all_images.extend(page_images)

                pages_data.append(
                    {
                        "page_num": page_num + 1,
                        "text": page_text,
                        "images": page_images,
                        "char_count": len(page_text),
                    }
                )

            full_text = "\n\n".join(all_text_parts)
            doc.close()

            result = {
                "text": full_text,
                "pages": pages_data,
                "metadata": {
                    "source": filename,
                    "type": "pdf",
                    "total_pages": len(pages_data),
                    "total_chars": len(full_text),
                    "has_images": len(all_images) > 0,
                    "image_count": len(all_images),
                },
                "images": all_images,
            }

            logger.info(
                f"PDF processed: {filename} | "
                f"{len(pages_data)} pages, {len(full_text)} chars, {len(all_images)} images"
            )
            return result

        except Exception as e:
            logger.error(f"PDF processing failed for {filename}: {e}")
            raise

    def _extract_page_images(
        self, page: fitz.Page, doc: fitz.Document
    ) -> List[Image.Image]:
        """Extract images from a PDF page."""
        images = []
        try:
            image_list = page.get_images(full=True)
            for img_info in image_list:
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    if base_image:
                        image_bytes = base_image["image"]
                        img = Image.open(io.BytesIO(image_bytes))

                        # Filter out tiny images (icons, bullets, etc.)
                        if (
                            img.width >= MIN_IMAGE_SIZE[0]
                            and img.height >= MIN_IMAGE_SIZE[1]
                        ):
                            # Convert to RGB if needed
                            if img.mode not in ("RGB", "RGBA"):
                                img = img.convert("RGB")
                            images.append(img)
                except Exception as e:
                    logger.debug(f"Failed to extract image xref={xref}: {e}")
                    continue
        except Exception as e:
            logger.debug(f"Failed to get image list from page: {e}")

        return images

    def get_page_chunks(
        self,
        result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Convert processed PDF result into per-page chunks with metadata.
        Each chunk includes the page text and associated images.
        """
        chunks = []
        for page_data in result["pages"]:
            if not page_data["text"].strip():
                continue
            chunks.append(
                {
                    "content": page_data["text"],
                    "images": page_data["images"],
                    "metadata": {
                        "source": result["metadata"]["source"],
                        "type": "pdf",
                        "page": page_data["page_num"],
                        "has_images": len(page_data["images"]) > 0,
                    },
                }
            )
        return chunks
