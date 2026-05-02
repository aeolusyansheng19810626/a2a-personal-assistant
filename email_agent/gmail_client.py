import os
import base64
from email.mime.text import MIMEText
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailClient:
    def __init__(self, credentials_path: str = "../credentials.json", token_path: str = "email_token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def list_emails(self, max_results: int = 10, query: str = "") -> List[Dict]:
        """List emails from inbox"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            email_list = []
            for msg in messages:
                email_data = self.get_email(msg['id'])
                if email_data:
                    email_list.append(email_data)
            
            return email_list
        
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def get_email(self, message_id: str) -> Optional[Dict]:
        """Get a specific email by ID"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
            
            # Get email body
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
            
            return {
                'id': message_id,
                'subject': subject,
                'from': sender,
                'date': date,
                'snippet': message.get('snippet', ''),
                'body': body[:500] if body else message.get('snippet', '')  # Limit body length
            }
        
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def send_email(self, to: str, subject: str, body: str) -> Dict:
        """Send an email"""
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'id': send_message['id'],
                'to': to,
                'subject': subject
            }
        
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search emails with a query"""
        return self.list_emails(max_results=max_results, query=query)

# Made with Bob
