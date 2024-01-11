from myproject.helpers import parse_rss_feeds, parse_html_content
from myproject.models import News
from myproject import db


def fetch_news():
    feed_title, entries = parse_rss_feeds('https://www.ntv.com.tr/ekonomi.rss')
    for entry in entries:
        entry["subtitle"], entry["image_url"], entry["details"] = parse_html_content(entry.summary)

        news = News(entry['title'], entry['subtitle'], entry["published"],
                    entry['image_url'], entry['details'], entry['link'])
        if not News.query.filter_by(title=news.title).first():
            db.session.add(news)
        else:
            print("fetched before")
    db.session.commit()
