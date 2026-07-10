import fitz  # PyMuPDF
from fastapi import HTTPException, status

class PdfService:
    @staticmethod
    def validate_and_extract(file_bytes: bytes, filename: str) -> str:
        """
        Validates that the file is a PDF and extracts its text contents using PyMuPDF.
        Raises HTTPException if file is invalid, empty, or corrupted.
        """
        # 1. Validate file extension
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Only PDF resumes are supported."
            )

        # 2. Validate PDF signature (Magic bytes check)
        if len(file_bytes) < 4 or file_bytes[:4] != b"%PDF":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid PDF or is corrupted."
            )

        try:
            # Load PDF directly from memory stream
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read PDF document. It may be corrupted: {str(e)}"
            )

        # 3. Check for empty pages structure
        if len(doc) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF resume contains no pages."
            )

        # 4. Extract text page by page
        extracted_text_parts = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                extracted_text_parts.append(text)

        raw_text = "\n".join(extracted_text_parts).strip()

        # 5. Check if the text is completely blank (e.g. image-only PDF without OCR)
        if not raw_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The PDF resume contains no readable text. Please upload a text-based PDF."
            )

        return raw_text
