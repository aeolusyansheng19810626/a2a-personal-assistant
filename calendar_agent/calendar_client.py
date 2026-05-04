import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

class CalendarClient:
    def __init__(self, credentials_path: str = "../credentials.json", token_path: str = "calendar_token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """OAuth2を使用してGoogle Calendar APIで認証"""
        creds = None
        
        # 既存のトークンを読み込み
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # 有効な認証情報がない場合は認証を実行
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
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def list_events(self, max_results: int = 10, time_min: Optional[str] = None) -> List[Dict]:
        """今後のカレンダーイベントを一覧表示"""
        try:
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                event_list.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })
            
            return event_list
        
        except HttpError as error:
            raise Exception(f"Calendar API error: {error}")
    
    def create_event(self, summary: str, start_time: str, end_time: str,
                     description: str = "", location: str = "") -> Dict:
        """カレンダーイベントを作成"""
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'Asia/Tokyo',
                },
            }
            
            if location:
                event['location'] = location
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'id': created_event['id'],
                'summary': created_event['summary'],
                'start': created_event['start']['dateTime'],
                'end': created_event['end']['dateTime'],
                'link': created_event.get('htmlLink', '')
            }
        
        except HttpError as error:
            raise Exception(f"Calendar API error: {error}")
    
    def get_today_schedule(self) -> List[Dict]:
        """今日のスケジュールを取得"""
        try:
            # 今日の開始時刻
            now = datetime.utcnow()
            start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_of_day = start_of_day + timedelta(days=1)
            
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                event_list.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })
            
            return event_list
        
        except HttpError as error:
            raise Exception(f"Calendar API error: {error}")
    
    def get_event(self, event_id: str) -> Optional[Dict]:
        """IDで特定のイベントを取得"""
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            return {
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'start': start,
                'end': end,
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'link': event.get('htmlLink', '')
            }
        
        except HttpError as error:
            raise Exception(f"Calendar API error: {error}")

