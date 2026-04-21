import requests, json, os
from datetime import datetime, timezone

ZENDESK_URL = "https://help.puzzel.com/api/v2/help_center/en-us/sections/29885/articles.json"
SLACK_WEBHOOK = os.environ["SLACK_WEBHOOK_URL"]
SEEN_FILE = "last_seen_article.json"

def get_latest_article():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(ZENDESK_URL, headers=headers, params={"sort_by": "created_at", "sort_order": "desc", "per_page": 1})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    return articles[0] if articles else None

def load_last_seen():
    try:
        with open(SEEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_last_seen(article):
    with open(SEEN_FILE, "w") as f:
        json.dump({"id": article["id"], "created_at": article["created_at"]}, f)

def post_to_slack(article):
    message = {
        "text": f":newspaper: *New Puzzel Release Note*\n*<{article['html_url']}|{article['title']}>*\nPublished: {article['created_at'][:10]}"
    }
    requests.post(SLACK_WEBHOOK, json=message)

def main():
    latest = get_latest_article()
    if not latest:
        return

    last_seen = load_last_seen()
    if last_seen is None or latest["id"] != last_seen["id"]:
        post_to_slack(latest)
        save_last_seen(latest)
        print(f"Posted: {latest['title']}")
    else:
        print("No new articles.")

if __name__ == "__main__":
    main()
