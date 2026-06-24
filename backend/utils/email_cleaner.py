import re
from bs4 import BeautifulSoup
import html

def clean_email_body(raw_html: str) -> str:
    """
    Strips all HTML tags, removes <style> and <script> blocks, 
    removes URLs/links, and collapses whitespace to create a clean, 
    token-efficient plain text string for the LLM.
    """
    if not raw_html:
        return ""

    # Decode HTML entities
    text = html.unescape(raw_html)

    # Use BeautifulSoup to safely parse and strip HTML
    try:
        soup = BeautifulSoup(text, 'html.parser')
        
        # Remove script and style elements completely
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get plain text
        text = soup.get_text(separator=' ')
    except Exception:
        # Fallback to regex if BeautifulSoup fails
        text = re.sub(r'<style.*?</style>', ' ', text, flags=re.IGNORECASE|re.DOTALL)
        text = re.sub(r'<script.*?</script>', ' ', text, flags=re.IGNORECASE|re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)

    # Replace long URLs (http://... or https://...) with a generic [link] placeholder
    # This saves massive amounts of tokens from tracking links
    text = re.sub(r'https?:\/\/\S+', '[link]', text)
    
    # Remove large blocks of empty space/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
