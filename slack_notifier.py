import requests
import json
from config import SLACK_WEBHOOK_URL

class SlackNotifier:
    @staticmethod
    def send_message(message, is_complete=False):
        if not SLACK_WEBHOOK_URL:
            print("Slack webhook not configured. Message:", message)
            return
        
        payload = {
            "text": message,
            "username": "Recon Bot",
            "icon_emoji": ":mag:"
        }
        
        if is_complete:
            payload['attachments'] = [{
                "color": "#36a64f",
                "title": "Scan Complete",
                "text": message
            }]
        
        try:
            response = requests.post(
                SLACK_WEBHOOK_URL,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                print(f"Failed to send Slack notification: {response.text}")
        except Exception as e:
            print(f"Error sending Slack notification: {e}")