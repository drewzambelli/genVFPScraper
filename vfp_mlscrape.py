import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL and article range
base_url = "http://www.ml-consult.co.uk/foxst-"
article_numbers = range(1, 48)  # Modify as needed

# Create base directory
base_folder = "scraped_mlarticles"
os.makedirs(base_folder, exist_ok=True)

def sanitize_filename(name):
    """Sanitize a string to be a valid filename."""
    sanitized_name = re.sub(r'[\/:*?"<>|\\\n\r]', '', name)
    return sanitized_name.replace(' ', '_')


def download_image(img_url, article_title, img_number):
    """Downloads and saves an image, returning the new local path."""
    if not img_url:
        return None

    # Extract file extension
    ext = os.path.splitext(img_url)[-1] or ".jpg"

    # Format image name
    img_name = f"{sanitize_filename(article_title)}_img{img_number}{ext}"
    img_path = os.path.join(base_folder, "images", img_name)

    try:
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            with open(img_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return f"images/{img_name}"  # Markdown relative path
    except requests.RequestException as e:
        print(f"Failed to download {img_url}: {e}")
    return None

def scrape_article(article_number):
    """Scrapes an article, extracts images and code, and saves it in Markdown format."""
    url = f"{base_url}{article_number:02d}.htm" #02d means 2 digit
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve: {url}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Find article container
        article_div = soup.find("div", class_="article")
        if not article_div:
            print(f"No article content found for article {article_number}")
            return

        # Extract title from <h1> inside <div class="article">
        title_tag = article_div.find("h1")
        article_title = title_tag.get_text(strip=True) if title_tag else f"Article_{article_number}"
        safe_title = sanitize_filename(article_title)

        # Extract text, preserving code blocks
        content = []
        for tag in article_div.find_all(["p", "pre", "code"]):
            if tag.name in ["pre", "code"]:
                content.append(f"```\n{tag.get_text()}\n```")
            else:
                content.append(tag.get_text())

        # Extract and download only images inside <div class="article">
        img_count = 1
        for img in article_div.find_all("img"):
            img_url = urljoin(url, img.get("src", ""))  # Handle missing src
            if img_url:
                local_img_path = download_image(img_url, article_title, img_count)
                if local_img_path:
                    content.append(f"![Image]({local_img_path})")
                    img_count += 1

        # Save article as Markdown using the article title
        article_filename = f"{safe_title}.md"
        article_path = os.path.join(base_folder, article_filename)
        with open(article_path, "w", encoding="utf-8") as file:
            file.write(f"# {article_title}\n\n" + "\n\n".join(content))

        print(f"Saved: {article_path}")

    except requests.RequestException as e:
        print(f"Error fetching article {article_number}: {e}")

# Loop through all articles and scrape them
for num in article_numbers:
    scrape_article(num)

print("Scraping completed.")
