import feedparser
from bs4 import BeautifulSoup


def parse_html_content(html_content):

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract subtitle (first <p>)
    subtitle = soup.find('p').text

    # Extract image URL
    image_url = soup.find('img')['src']

    # Extract details (rest of the <p> elements)
    details = ''.join([p.text for p in soup.find_all('p')[1:]])

    """
    print("Subtitle:", subtitle)
    print("\nImage URL:", image_url)
    print("\nDetails:", details)
    """
    return subtitle, image_url, details

def parse_rss_feeds(rss_feed_url):
    # Fetch the RSS feed
    feed = feedparser.parse(rss_feed_url)
    # Extract relevant information from the feed
    entries = feed.entries

    # Enhance each entry with an image URL from the article's content
    #for entry in entries:
    #   entry['image_url'] = get_image_url(entry)

    return entries