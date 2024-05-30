import os.path
import pickle
import redis
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from .models import Email
import time
import threading
import sched
from bs4 import BeautifulSoup

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "D:/EmailClassify/EmailClassifier/Email/credentials.json"
TOKEN_FILE = "D:/EmailClassify/EmailClassifier/Email/token.pickle"

def fetch_email():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me").execute()
        messages = results.get("messages", [])
        if not messages:
            print("No new messages found.")
            return []

        email_data = []
        new_messages = False
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"], format='full').execute()
            headers = msg["payload"]["headers"]
            try:
                x = msg.get('payload').get('parts')[1].get('body').get('data')
                decoded_x = base64.urlsafe_b64decode(x).decode('utf-8')
            except AttributeError as e:
                print(f"Error accessing data: {e}")
            except IndexError as e:
                print(f"Error accessing index: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            From = next((header["value"] for header in headers if header["name"] == "From"), "")
            To = next((header["value"] for header in headers if header["name"] == "To"), "")
            subject = [header["value"] for header in headers if header["name"] == "Subject"][0]
            payload = msg["payload"]
            if "parts" in payload:
                parts = payload["parts"]
                for part in parts:
                    if part["mimeType"] == "text/plain":
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        email_data.append({"from": From, "to": To,"subject": subject, "body": body, "predicted_class": None, "priority": None,"decoded_mail": decoded_x, "escalation": None})
                        email, created = Email.objects.get_or_create(From=From, To=To,subject=subject, defaults={'body': body})
                        if created:
                            new_messages = True
                            print("New message found:", subject)
                        # soup = BeautifulSoup(body, 'html.parser')
                        # text = soup.get_text()
                        # print("Text Html \n")
                        # print(text)

                        break

        r.set('emails', pickle.dumps(email_data))
        print("Updated cache with new emails.")

        return email_data

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def update_cache(scheduler):
    email_data = fetch_email()
    r.set('emails', pickle.dumps(email_data))
    print("Updated cache with new emails.")
    scheduler.enter(120, 1, update_cache, (scheduler,))

def start_cache_update():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 1, update_cache, (scheduler,))
    scheduler.run()

update_cache_thread = threading.Thread(target=start_cache_update)
update_cache_thread.start()

def get_cached_emails():
    emails = r.get('emails')
    if emails:
        email_list = pickle.loads(emails)
        print("Cached emails:", email_list)
        return email_list
    print("No cached emails found.")
    return []

