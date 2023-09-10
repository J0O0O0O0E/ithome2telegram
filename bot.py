import feedparser
import requests
import schedule
import time
import logging
from bs4 import BeautifulSoup
from http.client import IncompleteRead

logging.basicConfig(level=logging.INFO)

# Store the links of the news that have been sent
sent_news = set()

def send_to_telegram(title, summary, link, image_url):
    bot_token = '<your-bot-token>'
    channel_id = '<your-channel-id>'
    text = f'<b>{title}</b>\n\n{summary}\n<a href="{link}">阅读更多</a>'
    payload = {
        'chat_id': channel_id,
        'caption': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    if image_url:
        payload['photo'] = image_url
        method = 'sendPhoto'
    else:
        payload['text'] = text
        method = 'sendMessage'
    try:
        requests.post(f'https://api.telegram.org/bot{bot_token}/{method}', data=payload)
        logging.info(f'Sent message: {title}')
    except Exception as e:
        logging.error(f'Failed to send message: {title}. Error: {e}')

def parse_feed():
    try:
        NewsFeed = feedparser.parse("https://www.ithome.com/rss/")
        for entry in NewsFeed.entries:
            # Skip the news that has been sent
            if entry.link in sent_news:
                continue
            title = entry.title
            soup = BeautifulSoup(entry.description, 'html.parser')
            paragraphs = soup.find_all('p')
            summary = '\n'.join(p.get_text() for p in paragraphs[:2])
            link = entry.link
            # Get the first image in the news
            image_url = soup.find('img')['src'] if soup.find('img') else None
            send_to_telegram(title, summary, link, image_url)
            # Mark this news as sent
            sent_news.add(entry.link)
    except IncompleteRead as e:
        logging.error(f'Failed to read RSS feed. Error: {e}')

if __name__ == "__main__":
    schedule.every(300).seconds.do(parse_feed)
    while True:
        schedule.run_pending()
        time.sleep(1)
