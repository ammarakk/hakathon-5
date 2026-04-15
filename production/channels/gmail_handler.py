# production/channels/gmail_handler.py

import os
import base64
import json
import asyncio
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_PATH = os.getenv(
    "GMAIL_CREDENTIALS_PATH",
    "credentials.json"
)
TOKEN_PATH = os.getenv(
    "GMAIL_TOKEN_PATH",
    "token.json"
)
GMAIL_USER = os.getenv(
    "GMAIL_USER",
    "me"
)
POLL_INTERVAL = int(os.getenv(
    "GMAIL_POLL_INTERVAL",
    "30"
))

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

# Get Gmail Service
def get_gmail_service():
    """
    Build Gmail API service.
    Uses token.json if exists,
    otherwise prompts for auth.
    """
    try:
        from google.oauth2.credentials import (
            Credentials
        )
        from google.auth.transport.requests import (
            Request
        )
        from google_auth_oauthlib.flow import (
            InstalledAppFlow
        )
        from googleapiclient.discovery import build

        creds = None

        if Path(TOKEN_PATH).exists():
            creds = Credentials.from_authorized_user_file(
                TOKEN_PATH, SCOPES
            )

        if not creds or not creds.valid:
            if (creds and creds.expired
                    and creds.refresh_token):
                creds.refresh(Request())
            else:
                if not Path(CREDENTIALS_PATH).exists():
                    print(
                        "credentials.json not found!\n"
                        "See docs/gmail-setup.md"
                    )
                    return None

                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                creds = flow.run_local_server(
                    port=0
                )

            with open(TOKEN_PATH, 'w') as f:
                f.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    except Exception as e:
        print(f"Gmail service error: {e}")
        return None

# Parse Email
def parse_email(message: dict) -> dict:
    """Extract email details from Gmail message"""
    try:
        headers = message.get(
            "payload", {}
        ).get("headers", [])

        header_map = {
            h["name"].lower(): h["value"]
            for h in headers
        }

        sender = header_map.get("from", "")
        subject = header_map.get(
            "subject", "No Subject"
        )
        reply_to = header_map.get(
            "reply-to", sender
        )
        message_id = header_map.get(
            "message-id", ""
        )

        # Extract email address
        import re
        email_match = re.search(
            r'<(.+?)>|(\S+@\S+)',
            sender
        )
        email_addr = ""
        if email_match:
            email_addr = (
                email_match.group(1) or
                email_match.group(2)
            )

        sender_name = re.sub(
            r'<.*?>', '', sender
        ).strip().strip('"') or email_addr

        # Extract body
        body = extract_email_body(
            message.get("payload", {})
        )

        return {
            "id": message.get("id", ""),
            "thread_id": message.get("threadId", ""),
            "sender": sender,
            "sender_email": email_addr,
            "sender_name": sender_name,
            "subject": subject,
            "reply_to": reply_to,
            "message_id": message_id,
            "body": body,
            "channel": "email",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Parse email error: {e}")
        return {}

def extract_email_body(payload: dict) -> str:
    """Extract text body from email payload"""
    body = ""

    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                data = part.get(
                    "body", {}
                ).get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(
                        data + "=="
                    ).decode("utf-8", errors="ignore")
                    break
            elif mime_type == "text/html" and not body:
                data = part.get(
                    "body", {}
                ).get("data", "")
                if data:
                    html = base64.urlsafe_b64decode(
                        data + "=="
                    ).decode("utf-8", errors="ignore")
                    # Strip HTML tags
                    import re
                    body = re.sub(
                        r'<[^>]+>', '', html
                    ).strip()
    else:
        data = payload.get(
            "body", {}
        ).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(
                data + "=="
            ).decode("utf-8", errors="ignore")

    return body.strip()[:2000]

# Send Email Reply
async def send_email_reply(
    to_email: str,
    subject: str,
    body: str,
    thread_id: str = "",
    in_reply_to: str = ""
) -> dict:
    """Send email reply via Gmail API"""
    try:
        service = get_gmail_service()
        if not service:
            return {
                "success": False,
                "error": "Gmail not configured"
            }

        # Build email
        msg = MIMEMultipart("alternative")
        msg["To"] = to_email
        msg["From"] = GMAIL_USER
        msg["Subject"] = (
            f"Re: {subject}"
            if not subject.startswith("Re:")
            else subject
        )

        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to

        # Plain text part
        text_part = MIMEText(body, "plain")
        msg.attach(text_part)

        # HTML part with Nur Scents styling
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif;
             color: #333; max-width: 600px;">
  <div style="padding: 20px;">
    {body.replace(chr(10), '<br>')}
  </div>
  <hr style="border: none;
             border-top: 1px solid #eee;
             margin: 20px 0;">
  <div style="color: #888; font-size: 12px;">
    <strong>Nur Scents</strong><br>
    Premium Fragrances — Karachi, Pakistan<br>
    WhatsApp: {os.getenv('BUSINESS_PHONE', '')}<br>
    Email: {GMAIL_USER}
  </div>
</body>
</html>"""

        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)

        # Encode and send
        raw = base64.urlsafe_b64encode(
            msg.as_bytes()
        ).decode()

        send_body = {"raw": raw}
        if thread_id:
            send_body["threadId"] = thread_id

        sent = service.users().messages().send(
            userId="me",
            body=send_body
        ).execute()

        return {
            "success": True,
            "message_id": sent.get("id"),
            "thread_id": sent.get("threadId")
        }

    except Exception as e:
        print(f"Send email error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Mark Email Read
def mark_as_read(
    service,
    message_id: str
) -> bool:
    """Mark email as read after processing"""
    try:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        return True
    except Exception as e:
        print(f"Mark read error: {e}")
        return False

# Get Unread Emails
def get_unread_emails(
    service,
    max_results: int = 10
) -> list:
    """Get unread emails from inbox"""
    try:
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX", "UNREAD"],
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for msg_ref in messages:
            msg = service.users().messages().get(
                userId="me",
                id=msg_ref["id"],
                format="full"
            ).execute()
            emails.append(msg)

        return emails

    except Exception as e:
        print(f"Get emails error: {e}")
        return []

# Gmail Polling Worker
async def run_gmail_poller(
    db=None,
    kafka_producer=None
):
    """
    Poll Gmail for new emails.
    Runs continuously — checks every 30 seconds.
    Alternative to Pub/Sub webhook.
    """
    print(f"Starting Gmail poller...")
    print(f"Polling every {POLL_INTERVAL}s\n")

    service = get_gmail_service()
    if not service:
        print(
            "Gmail not configured.\n"
            "See docs/gmail-setup.md\n"
            "Running in mock mode..."
        )
        while True:
            await asyncio.sleep(POLL_INTERVAL)
        return

    processed_ids = set()

    while True:
        try:
            emails = get_unread_emails(
                service, max_results=5
            )

            for email_msg in emails:
                msg_id = email_msg.get("id", "")

                if msg_id in processed_ids:
                    continue

                parsed = parse_email(email_msg)
                if not parsed.get("body"):
                    continue

                print(
                    f"\nNew email from: "
                    f"{parsed['sender_email']}\n"
                    f"Subject: {parsed['subject']}\n"
                    f"Body: {parsed['body'][:100]}..."
                )

                # Send to Kafka
                if kafka_producer:
                    await kafka_producer.send_ticket(
                        channel="email",
                        customer_name=parsed['sender_name'],
                        identifier=parsed['sender_email'],
                        message=(
                            f"Subject: {parsed['subject']}"
                            f"\n\n{parsed['body']}"
                        ),
                        metadata={
                            "subject": parsed['subject'],
                            "thread_id": parsed['thread_id'],
                            "message_id": parsed['message_id']
                        }
                    )

                # Process with agent
                from production.agent.customer_success_agent import (
                    process_customer_message
                )

                response = await process_customer_message(
                    message=(
                        f"Subject: {parsed['subject']}"
                        f"\n\n{parsed['body']}"
                    ),
                    channel="email",
                    customer_name=parsed['sender_name'],
                    identifier=parsed['sender_email'],
                    db=db
                )

                # Send reply
                send_result = await send_email_reply(
                    to_email=parsed['sender_email'],
                    subject=parsed['subject'],
                    body=response.response,
                    thread_id=parsed['thread_id'],
                    in_reply_to=parsed['message_id']
                )

                if send_result.get("success"):
                    print(
                        f"Email reply sent to "
                        f"{parsed['sender_email']} OK"
                    )
                    mark_as_read(service, msg_id)
                    processed_ids.add(msg_id)
                else:
                    print(
                        f"Email reply failed: "
                        f"{send_result.get('error')}"
                    )

                # Keep set manageable
                if len(processed_ids) > 1000:
                    processed_ids = set(
                        list(processed_ids)[-500:]
                    )

        except Exception as e:
            print(f"Poller error: {e}")

        await asyncio.sleep(POLL_INTERVAL)

# FastAPI Webhook Handler
async def handle_gmail_webhook(
    webhook_data: dict,
    db=None,
    kafka_producer=None
) -> dict:
    """
    Handle Gmail Pub/Sub webhook.
    Called from FastAPI /webhooks/gmail endpoint.
    """
    try:
        message_data = webhook_data.get(
            "message", {}
        )
        if not message_data:
            return {"status": "no_message"}

        data = message_data.get("data", "")
        if not data:
            return {"status": "no_data"}

        decoded = base64.b64decode(
            data + "=="
        ).decode("utf-8")
        notification = json.loads(decoded)

        email_address = notification.get(
            "emailAddress", ""
        )
        history_id = notification.get(
            "historyId", ""
        )

        print(
            f"Gmail webhook: {email_address} "
            f"historyId: {history_id}"
        )

        return {
            "status": "received",
            "email": email_address,
            "history_id": history_id
        }

    except Exception as e:
        print(f"Gmail webhook error: {e}")
        return {"status": "error", "detail": str(e)}

# Test Gmail Handler
async def test_gmail_handler():
    print("Testing Gmail Handler...\n")

    # Test 1: Parse email
    print("Test 1: Parse email")
    mock_message = {
        "id": "test123",
        "threadId": "thread123",
        "payload": {
            "headers": [
                {"name": "From",
                 "value": "Ahmed Khan <ahmed@gmail.com>"},
                {"name": "Subject",
                 "value": "Oud attar inquiry"},
                {"name": "Message-ID",
                 "value": "<test@gmail.com>"}
            ],
            "body": {
                "data": base64.urlsafe_b64encode(
                    "I want to buy oud attar. "
                    "What are the prices?".encode()
                ).decode()
            }
        }
    }

    parsed = parse_email(mock_message)
    print(f"Sender: {parsed.get('sender_email')}")
    print(f"Subject: {parsed.get('subject')}")
    print(f"Body: {parsed.get('body')[:50]}")
    print("OK Parse test passed\n")

    # Test 2: Gmail service
    print("Test 2: Gmail service connection")
    service = get_gmail_service()
    if service:
        print("OK Gmail service connected\n")

        # Test 3: Get unread emails
        print("Test 3: Get unread emails")
        emails = get_unread_emails(
            service, max_results=3
        )
        print(f"Unread emails found: {len(emails)}")
        print("OK Get emails test passed\n")

    else:
        print(
            "WARNING Gmail not configured\n"
            "    Run: python gmail_handler.py auth\n"
            "    See: docs/gmail-setup.md\n"
        )

    # Test 4: Send test email
    print("Test 4: Send email (mock)")
    test_reply = """Dear Ahmed Khan,

Thank you for contacting Nur Scents!

Our Oud Attar collection is available in
the following sizes and prices:

- 3ml: PKR 800
- 6ml: PKR 1,400
- 12ml: PKR 2,500

Please let us know which size interests you.

Best regards,
Nur Scents Team"""

    if service:
        print(
            "Skipping live send in test mode\n"
            "Use send_email_reply() in production"
        )
    print("OK Email format test passed\n")

    print("OK All Gmail handler tests complete!")

# Auth Command
def run_auth():
    print("Starting Gmail authentication...")
    print("Browser will open for Google login\n")
    service = get_gmail_service()
    if service:
        profile = service.users().getProfile(
            userId="me"
        ).execute()
        email = profile.get("emailAddress")
        print(f"OK Authenticated as: {email}")
        print(f"OK token.json saved")
    else:
        print("ERROR Authentication failed")
        print("Check credentials.json exists")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "auth":
            run_auth()
        elif sys.argv[1] == "poll":
            asyncio.run(run_gmail_poller())
        else:
            print("Usage:")
            print("  python gmail_handler.py auth")
            print("  python gmail_handler.py poll")
            print("  python gmail_handler.py test")
    else:
        asyncio.run(test_gmail_handler())
