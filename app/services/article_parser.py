import logging
import httpx
from bs4 import BeautifulSoup
from typing import Optional
from io import BytesIO
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def _is_pdf_url(url: str) -> bool:
    """
    Check if the URL points to a PDF file.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL appears to be a PDF, False otherwise
    """
    url_lower = url.lower()
    # Check if URL ends with .pdf
    if url_lower.endswith('.pdf'):
        return True
    
    # Check if URL contains .pdf in the path
    parsed = urlparse(url)
    if '.pdf' in parsed.path.lower():
        return True
    
    return False


async def _extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Extracted text content or None if extraction fails
    """
    try:
        from pypdf import PdfReader
        
        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        
        text_parts = []
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                continue
        
        if text_parts:
            full_text = "\n\n".join(text_parts)
            # Clean up excessive whitespace
            full_text = " ".join(full_text.split())
            return full_text if full_text else None
        
        return None
        
    except ImportError:
        logger.error("pypdf library is not installed. Cannot extract PDF content.")
        raise ImportError("pypdf library is required for PDF parsing. Install it with: poetry add pypdf")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return None


async def _extract_text_from_html(response: httpx.Response) -> Optional[str]:
    """
    Extract text content from an HTML response.
    
    Args:
        response: HTTP response object
        
    Returns:
        Extracted text content or None if extraction fails
    """
    soup = BeautifulSoup(response.text, "lxml")
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    
    # Try to find main content area
    # For PMC articles, look for specific content sections
    main_content = (
        soup.find("div", class_="tsec sec") or
        soup.find("div", id="maincontent") or
        soup.find("div", class_="article-content") or
        soup.find("article") or
        soup.find("main") or
        soup.find("div", class_="content")
    )
    
    if main_content:
        text = main_content.get_text(separator=" ", strip=True)
    else:
        # Fallback to body text, but exclude navigation and footer
        body = soup.find("body")
        if body:
            # Remove common non-content elements
            for elem in body.find_all(["nav", "header", "footer", "aside"]):
                elem.decompose()
            text = body.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)
    
    # Clean up excessive whitespace
    text = " ".join(text.split())
    
    return text if text else None


async def fetch_article_content(url: str) -> Optional[str]:
    """
    Fetches and extracts text content from an article URL.
    Supports both HTML web pages and PDF files.
    
    Args:
        url: URL of the article (can be HTML or PDF)
        
    Returns:
        Extracted text content or None if extraction fails
    """
    # Check if URL is a PDF
    is_pdf = _is_pdf_url(url)
    
    # Basic browser-like headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" if not is_pdf else "application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True) as client:
        response = await client.get(str(url))
        response.raise_for_status()
        
        # Check content type to determine if it's a PDF
        content_type = response.headers.get("content-type", "").lower()
        is_pdf_response = is_pdf or "application/pdf" in content_type
        
        if is_pdf_response:
            return await _extract_text_from_pdf(response.content)
        else:
            return await _extract_text_from_html(response)

