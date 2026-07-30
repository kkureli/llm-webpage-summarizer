from bs4 import BeautifulSoup
import requests
from requests.exceptions import SSLError
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

MAX_CHARS = 12_000

# Noise to strip before reading content
NOISE_TAGS = [
    "script",
    "style",
    "noscript",
    "img",
    "input",
    "svg",
    "nav",
    "header",
    "footer",
    "aside",
    "form",
    "iframe",
]


def _get(url):
    """
    Fetch URL with SSL verify on; if the site has a broken cert chain
    (common with some CDNs), retry without verification.
    """
    try:
        return requests.get(url, headers=headers, timeout=30)
    except SSLError:
        return requests.get(url, headers=headers, timeout=30, verify=False)


def _clean_text(node) -> str:
    text = node.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def _main_content(soup: BeautifulSoup):
    """Prefer article/main content over the full page body (skips mega-menus)."""
    for selector in ("article", "main", '[role="main"]'):
        node = soup.select_one(selector)
        if node and _clean_text(node):
            return node
    return soup.body


def fetch_website_contents(url):
    """
    Return the title and main contents of the website at the given url.
    Navigation/chrome is stripped; text is truncated to MAX_CHARS.
    """
    response = _get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"

    root = _main_content(soup)
    if not root:
        return title

    for irrelevant in root(NOISE_TAGS):
        irrelevant.decompose()

    # Drop leftover menu-like blocks inside article/main
    for node in root.select('[role="navigation"], .nav, .menu, .navbar, .breadcrumb'):
        node.decompose()

    text = _clean_text(root)
    if not text and soup.body:
        for irrelevant in soup.body(NOISE_TAGS):
            irrelevant.decompose()
        text = _clean_text(soup.body)

    return (title + "\n\n" + text)[:MAX_CHARS]


def fetch_website_links(url):
    """
    Return the links on the website at the given url.
    """
    response = _get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]
