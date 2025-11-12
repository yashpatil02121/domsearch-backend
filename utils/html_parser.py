from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

def extract_clean_text(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles, etc.
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)

def extract_text_with_structure(url: str) -> list:
    """Extract text chunks with their DOM path and HTML structure"""
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Remove scripts, styles, etc.
    for tag in soup(["script", "style", "noscript", "meta", "link"]):
        tag.decompose()
    
    parsed_url = urlparse(url)
    base_path = parsed_url.path.strip('/') if parsed_url.path and parsed_url.path != '/' else "home"
    
    chunks_with_structure = []
    seen_texts = set()  # Avoid duplicate content
    
    # Extract main content sections with their HTML
    # Prioritize semantic HTML elements
    content_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'div', 'section', 'article', 'main'])
    
    for tag in content_tags:
        text = tag.get_text(separator=" ", strip=True)
        
        # Only meaningful content, avoid duplicates
        if text and len(text) > 30 and text not in seen_texts:
            seen_texts.add(text)
            
            # Get clean HTML snippet
            html_snippet = str(tag)
            
            # Clean up the HTML for display
            # Remove excessive whitespace
            html_snippet = ' '.join(html_snippet.split())
            
            # Limit HTML snippet size but keep it readable
            if len(html_snippet) > 1000:
                html_snippet = html_snippet[:1000] + "..."
            
            # Try to extract a path or identifier
            tag_id = tag.get('id', '')
            tag_class = ' '.join(tag.get('class', []))
            
            chunks_with_structure.append({
                'text': text,
                'html': html_snippet,
                'path': base_path,
                'tag_id': tag_id,
                'tag_class': tag_class,
                'tag_name': tag.name
            })
    
    # If no structured content found, fall back to body text
    if not chunks_with_structure:
        body = soup.find('body')
        if body:
            text = body.get_text(separator=" ", strip=True)
            chunks_with_structure.append({
                'text': text,
                'html': str(body)[:1000],
                'path': base_path,
                'tag_id': '',
                'tag_class': '',
                'tag_name': 'body'
            })
    
    return chunks_with_structure
