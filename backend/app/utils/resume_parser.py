
from pypdf import PdfReader


# PDF PROCESSING LIMITS
MAX_PDF_PAGES = 30
MAX_EXTRACTED_CHARACTERS = 200_000


def extract_text_from_pdf(file_path: str) -> str:
    """
    Safely extract text from an uploaded PDF resume.

    Security:
    - Reject encrypted PDFs.
    - Limit the number of pages.
    - Limit total extracted text, including separators.
    - Handle malformed PDF files.
    """

    try:
        pdf_document = PdfReader(
            file_path,
            strict=True
        )

        # Reject password-protected PDFs
        if pdf_document.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        # Check PDF page count
        total_pages = len(pdf_document.pages)

        if total_pages == 0:
            raise ValueError(
                "The uploaded PDF contains no pages."
            )

        if total_pages > MAX_PDF_PAGES:
            raise ValueError(
                f"PDF cannot contain more than {MAX_PDF_PAGES} pages."
            )

        extracted_pages = []
        total_characters = 0

        # Extract text page by page
        for page in pdf_document.pages:

            # Account for the newline separator
            separator_size = 1 if extracted_pages else 0

            remaining_characters = (
                MAX_EXTRACTED_CHARACTERS
                - total_characters
                - separator_size
            )

            if remaining_characters <= 0:
                break

            page_text = page.extract_text() or ""

            page_text = page_text[:remaining_characters]

            extracted_pages.append(page_text)

            total_characters += separator_size + len(page_text)

        return "\n".join(extracted_pages).strip()

    except ValueError:
        raise

    except Exception:
        raise ValueError(
            "Could not read the uploaded PDF. "
            "Please upload a valid, readable PDF file."
        )
