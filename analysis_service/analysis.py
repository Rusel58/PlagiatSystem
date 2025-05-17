import hashlib
from wordcloud import WordCloud
import io

def compute_stats(text: str):
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])
    words = len(text.split())
    characters = len(text)
    return paragraphs, words, characters

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_wordcloud(text: str) -> bytes:
    wc = WordCloud(width=800, height=400).generate(text)
    buf = io.BytesIO()
    wc.to_image().save(buf, format="PNG")
    return buf.getvalue()