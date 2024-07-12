import requests
from bs4 import BeautifulSoup
import csv

def scrape_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    img_tag = soup.find('img', {'id': 'post_img'})
    img_url = img_tag['src'] if img_tag else 'No image'
    
    header_tag = soup.find('h1', {'class': 'top_stories_header_news'})
    header_text = header_tag.text.strip() if header_tag else 'No header'
    
    details_tag = soup.find('div', {'id': 'testId', 'class': 'new_details'})
    details_text = details_tag.text.strip() if details_tag else 'No details'
    
    return {
        'img_url': img_url,
        'header_text': header_text,
        'details_text': details_text
    }

def scrape_main_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles_data = []
    seen_headers = set()
    
    main_articles = soup.find_all('div', {'class': 'ng-star-inserted'})
    for article in main_articles:
        a_tag = article.find('a', href=True)
        if a_tag:
            article_url = a_tag['href']
            full_article_url = 'https://english.newsfirst.lk' + article_url
            article_data = scrape_article(full_article_url)
            
            if article_data['header_text'] not in seen_headers:
                seen_headers.add(article_data['header_text'])
                articles_data.append(article_data)
    
    local_news_section = soup.find('div', {'class': 'local_news'})
    if local_news_section:
        local_news_links = local_news_section.find_all('a', href=True, limit=4)
        for link in local_news_links:
            article_url = link['href']
            full_article_url = 'https://english.newsfirst.lk' + article_url
            article_data = scrape_article(full_article_url)
            
            if article_data['header_text'] not in seen_headers:
                seen_headers.add(article_data['header_text'])
                articles_data.append(article_data)
    
    return articles_data

main_url = 'https://english.newsfirst.lk/2024/07/09'
scraped_data = scrape_main_page(main_url)


csv_file_name = 'scraped_data.csv'


with open(csv_file_name, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['img_url', 'header_text', 'details_text'])
    writer.writeheader()
    for data in scraped_data:
        writer.writerow(data)

print(f"Scraped data has been saved to {csv_file_name}")
