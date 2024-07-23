import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os
import re
from deep_translator import GoogleTranslator

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BASE_URL = os.getenv("BASE_URL")

# Initialize Google Translator
translator = GoogleTranslator(source="en", target="si")


class DateModel(BaseModel):
    date: str


def translate_text(text):
    translated = translator.translate(text)
    return translated


def clean_text(text):
    # Define a list of unwanted keywords
    unwanted_keywords = ["COLOMBO", "News 1st", "(News 1st)"]
    for keyword in unwanted_keywords:
        text = re.sub(r"\b" + re.escape(keyword) + r"\b", "", text)
    # Remove unwanted characters and extra whitespace
    text = re.sub(r"[();]", "", text)
    text = " ".join(text.split())
    return text


def scrape_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    img_tag = soup.find("img", {"id": "post_img"})
    img_url = img_tag["src"] if img_tag else "No image"

    header_tag = soup.find("h1", {"class": "top_stories_header_news"})
    header_text = header_tag.text.strip() if header_tag else "No header"

    details_tag = soup.find("div", {"id": "testId", "class": "new_details"})
    details_text = details_tag.text.strip() if details_tag else "No details"

    # Clean the text
    header_text_clean = clean_text(header_text)
    details_text_clean = clean_text(details_text)

    # Translate the text to Sinhala
    header_text_translated = translate_text(header_text_clean)
    details_text_translated = translate_text(details_text_clean)

    return {
        "img_url": img_url,
        "header_text": header_text_translated,
        "details_text": details_text_translated,
    }


def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    articles_data = []
    seen_headers = set()
    seen_images = set()

    # main_articles = soup.find_all("div", {"class": "ng-star-inserted"})
    # for article in main_articles:
    #     a_tag = article.find("a", href=True)
    #     if a_tag:
    #         article_url = a_tag["href"]
    #         full_article_url = BASE_URL + article_url
    #         article_data = scrape_article(full_article_url)

    #         if (
    #             article_data["header_text"] not in seen_headers
    #             and article_data["img_url"] not in seen_images
    #         ):
    #             seen_headers.add(article_data["header_text"])
    #             seen_images.add(article_data["img_url"])
    #             articles_data.append(article_data)
                # break

    local_news_section = soup.find("div", {"class": "local_news"})
    if local_news_section:
        local_news_links = local_news_section.find_all("a", href=True, limit=5)
        for link in local_news_links:
            article_url = link["href"]
            full_article_url = BASE_URL + article_url
            article_data = scrape_article(full_article_url)

            if (
                article_data["header_text"] not in seen_headers
                and article_data["img_url"] not in seen_images
            ):
                seen_headers.add(article_data["header_text"])
                seen_images.add(article_data["img_url"])
                articles_data.append(article_data)

    return articles_data


@app.post("/scrape/")
async def scrape(request: Request, date: str = Form(...)):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    url = f"{BASE_URL}/{date.replace('-', '/')}"
    scraped_data = scrape_main_page(url)
    return templates.TemplateResponse(
        "index.html", {"request": request, "articles": scraped_data}
    )


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "articles": []}
    )


def escapejs_filter(value):
    escaped = (
        value.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("<", "\\u003C")
        .replace(">", "\\u003E")
        .replace("&", "\\u0026")
        .replace("=", "\\u003D")
    )
    return escaped


templates.env.filters["escapejs"] = escapejs_filter
