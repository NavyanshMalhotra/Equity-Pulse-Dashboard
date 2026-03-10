import os
import requests
import json
from dotenv import load_dotenv

# Import agentmail_client logic
import sys
sys.path.append("/data/copaw")
import agentmail_client

# Load environments
load_dotenv("/data/copaw/.env")
load_dotenv("/data/copaw/.env_github")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RECIPIENT_EMAIL = "malhotra15@hotmail.com"
INBOX_ID = "nm_copaw@agentmail.to"
STATE_FILE = "/data/copaw/openclaw_state.json"

def fetch_releases():
    url = "https://api.github.com/repos/OpenClaw/OpenClaw/releases"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching releases: {e}")
        return []

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
    return {"last_id": 0}

def save_state(last_id):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump({"last_id": last_id}, f)
    except Exception as e:
        print(f"Error saving state: {e}")

def monitor():
    releases = fetch_releases()
    if not releases:
        return

    state = load_state()
    last_id = state.get("last_id", 0)

    # Filter for new releases
    new_releases = [r for r in releases if r["id"] > last_id]

    if not new_releases:
        print("No new releases found.")
        return

    # Sort new releases by ID (oldest first)
    new_releases.sort(key=lambda x: x["id"])

    # Prepare email content
    count = len(new_releases)
    email_body = f"<h2>New OpenClaw Releases Detected ({count})</h2><hr>"
    
    for r in new_releases:
        tag = r.get("tag_name", "N/A")
        name = r.get("name") or tag
        published = r.get("published_at", "N/A")
        body = r.get("body", "No description provided.")
        url = r.get("html_url", "#")
        
        email_body += f"<h3>{name}</h3>"
        email_body += f"<p><b>Tag:</b> {tag}<br>"
        email_body += f"<b>Published:</b> {published}<br>"
        email_body += f"<b>URL:</b> <a href='{url}'>{url}</a></p>"
        email_body += f"<blockquote><pre style='background:#f0f0f0;padding:10px;'>{body[:1000]}{'...' if len(body) > 1000 else ''}</pre></blockquote><hr>"

    try:
        agentmail_client.send_message(
            inbox_id=INBOX_ID,
            to=RECIPIENT_EMAIL,
            subject=f"OpenClaw Alert: {count} New Release(s) Found",
            html=email_body
        )
        print(f"Success: Sent alert for {count} release(s) to {RECIPIENT_EMAIL}.")
        save_state(new_releases[-1]["id"])
    except Exception as e:
        print(f"Error sending alert: {e}")

if __name__ == "__main__":
    monitor()
