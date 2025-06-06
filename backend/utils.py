import os
import pickle
from dotenv import load_dotenv
from email.message import EmailMessage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64
import google.generativeai as genai

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gmail_service():
    creds = None
    token_file = 'token.pickle'

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("GMAIL_CREDENTIALS_FILE"), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def fetch_latest_email():
    try:
        service = get_gmail_service()
        result = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = result.get('messages', [])

        if not messages:
            return {"subject": "", "body": "No unread emails found.", "to": ""}

        msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        body = msg.get('snippet', '')

        return {"subject": subject, "body": body, "to": sender}
    except Exception as e:
        print("❌ Error fetching email:", e)
        return {"subject": "", "body": "Failed to fetch email.", "to": ""}

def generate_reply(subject, body):
    prompt = f"You received an email with subject: '{subject}' and body: '{body}'. Generate a polite, professional reply."
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def send_email(to, subject, body):
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = "me"
        message['Subject'] = f"Re: {subject}"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        service.users().messages().send(userId="me", body=create_message).execute()
        return True
    except Exception as e:
        print("❌ Error sending email:", e)
        return False

def fetch_emails(label_ids=['INBOX'], max_results=10):
    service = get_gmail_service()
    result = service.users().messages().list(
        userId='me',
        labelIds=label_ids,
        maxResults=max_results
    ).execute()

    messages = result.get('messages', [])
    emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        to = next((h['value'] for h in headers if h['name'] == 'To'), '')
        snippet = msg_detail.get('snippet', '')
        emails.append({
            'subject': subject,
            'from': sender,
            'to': to,
            'body': snippet
        })
    return emails
