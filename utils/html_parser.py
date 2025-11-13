from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse


# def extract_clean_text(url: str) -> str:
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")

#     for tag in soup(["script", "style", "noscript"]):
#         tag.decompose()

#     return soup.get_text(separator=" ", strip=True)


def extract_text_with_structure(url: str) -> list:
    # Uses a "browser-like" user-agent to avoid blocking. This is a common technique to avoid being blocked by websites.
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    # parse the response
    soup = BeautifulSoup(response.text, "html.parser")

    # remove unwanted tags
    for tag in soup(["script", "style", "noscript", "meta", "link"]):
        tag.decompose()

    # parse the url
    parsed_url = urlparse(url)
    base_path = parsed_url.path.strip('/') if parsed_url.path and parsed_url.path != '/' else "home"

    chunks_with_structure = []
    seen_texts = set()  # Avoid duplicates

    # Extract important DOM containers
    content_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'div', 'section', 'article', 'main'])

    for tag in content_tags:
        text = tag.get_text(separator=" ", strip=True)

        # Skip short/duplicate content
        if not text or len(text) < 10 or text in seen_texts:
            continue

        seen_texts.add(text)

        # Extract HTML snippet
        html_snippet = tag.prettify()

        # Truncate safely, take the first 800 characters
        if len(html_snippet) > 800:
            truncated = html_snippet[:800]

            # If cut ends mid-tag, remove the partial tag and truncate the rest
            if "<" in truncated[-40:] and ">" not in truncated[-20:]:
                truncated = truncated.rsplit("<", 1)[0]

            html_snippet = truncated + "\n..."

        # get the id, class and name of the tag (metadata for the chunk)
        tag_id = tag.get("id", "")
        tag_class = " ".join(tag.get("class", []))
        tag_name = tag.name

        chunks_with_structure.append({
            "text": text,
            "html": html_snippet,
            "path": base_path,
            "tag_id": tag_id,
            "tag_class": tag_class,
            "tag_name": tag_name
        })

    # Fallback: entire body
    if not chunks_with_structure:
        body = soup.find("body")
        if body:
            chunks_with_structure.append({
                "text": body.get_text(separator=" ", strip=True),
                "html": body.prettify()[:800] + "\n...",
                "path": base_path,
                "tag_id": "",
                "tag_class": "",
                "tag_name": "body"
            })

    return chunks_with_structure
