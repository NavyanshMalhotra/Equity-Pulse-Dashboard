import os
from agentmail import AgentMail
from dotenv import load_dotenv

load_dotenv()

AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")

if not AGENTMAIL_API_KEY:
    raise ValueError("AGENTMAIL_API_KEY is not set in the environment or .env file.")

client = AgentMail(api_key=AGENTMAIL_API_KEY)

def get_inboxes():
    return client.inboxes.list().inboxes

def list_messages(inbox_id, limit=50):
    return client.inboxes.messages.list(inbox_id, limit=limit).messages

def send_message(inbox_id, to, subject, text=None, html=None):
    if isinstance(to, str):
        to = [to]
        
    payload = {
        "to": to,
        "subject": subject,
    }
    if text:
        payload["text"] = text
    if html:
        payload["html"] = html
        
    return client.inboxes.messages.send(inbox_id, **payload)

if __name__ == "__main__":
    inboxes = get_inboxes()
    for inbox in inboxes:
        print(f"- {inbox.display_name} {vars(inbox)}")
