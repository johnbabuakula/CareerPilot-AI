
import pytest

import app.utils.resume_parser as resume_parser


# MOCK PDF PAGE
class MockPage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


# MOCK PDF DOCUMENT
class MockPDF:
    def __init__(self, pages, encrypted=False):
        self.pages = pages
        self.is_encrypted = encrypted


# 1. TEST SUCCESSFUL TEXT EXTRACTION
def test_extract_text_successfully(monkeypatch):

    mock_pdf = MockPDF([
        MockPage("Python Developer"),
        MockPage("SQL and FastAPI")
    ])

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        lambda *args, **kwargs: mock_pdf
    )

    result = resume_parser.extract_text_from_pdf("test.pdf")

    assert result == "Python Developer\nSQL and FastAPI"


# 2. TEST EMPTY PDF
def test_extract_text_from_empty_pdf(monkeypatch):

    mock_pdf = MockPDF([])

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        lambda *args, **kwargs: mock_pdf
    )

    with pytest.raises(
        ValueError,
        match="no pages"
    ):
        resume_parser.extract_text_from_pdf("test.pdf")


# 3. TEST ENCRYPTED PDF
def test_reject_encrypted_pdf(monkeypatch):

    mock_pdf = MockPDF(
        pages=[MockPage("Test")],
        encrypted=True
    )

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        lambda *args, **kwargs: mock_pdf
    )

    with pytest.raises(
        ValueError,
        match="Password-protected"
    ):
        resume_parser.extract_text_from_pdf("test.pdf")


# 4. TEST MAXIMUM PAGE LIMIT
def test_reject_pdf_with_too_many_pages(monkeypatch):

    mock_pages = [
        MockPage("Test page")
        for _ in range(31)
    ]

    mock_pdf = MockPDF(mock_pages)

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        lambda *args, **kwargs: mock_pdf
    )

    with pytest.raises(
        ValueError,
        match="30 pages"
    ):
        resume_parser.extract_text_from_pdf("test.pdf")


# 5. TEST MALFORMED PDF
def test_handle_malformed_pdf(monkeypatch):

    def raise_error(*args, **kwargs):
        raise RuntimeError("Invalid PDF")

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        raise_error
    )

    with pytest.raises(
        ValueError,
        match="Could not read the uploaded PDF"
    ):
        resume_parser.extract_text_from_pdf("test.pdf")


# 6. TEST EXTRACTED TEXT LIMIT
def test_limit_extracted_text(monkeypatch):

    mock_pdf = MockPDF([
        MockPage("A" * 150_000),
        MockPage("B" * 150_000)
    ])

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        lambda *args, **kwargs: mock_pdf
    )

    result = resume_parser.extract_text_from_pdf("test.pdf")

    assert len(result) == 200_000
    assert result.startswith("A")
    assert result.endswith("B")
