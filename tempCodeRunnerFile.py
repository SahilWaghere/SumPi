import imaplib
import email
from email.header import decode_header
import pyttsx3
import re
from fromscratch import summarize_text  # Import summarization function

# Email Credentials
EMAIL = "testsummarizer@gmail.com"
PASSWORD = "fvvi ixda ztlu oeis"  # Use an App Password if 2FA is enabled

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speech rate if needed
engine.setProperty('voice', engine.getProperty('voices')[0].id)  # Select default voice

def read_summary(text):
    """Reads out the given text using text-to-speech."""
    engine.say(text)
    engine.runAndWait()

def extract_name(sender):
    """Extracts the sender's name from the email address."""
    match = re.match(r'"?([\w\s]+)"?\s*<.*?>', sender)
    return match.group(1) if match else sender.split('@')[0]  # Fallback to username

# Connect to Gmail IMAP server
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL, PASSWORD)
mail.select("INBOX")  # Ensure correct folder selection

# Search for unread emails
status, messages = mail.search(None, "(UNSEEN)")
email_ids = messages[0].split()
print(f"Unread Emails Found: {len(email_ids)}")

if not email_ids:
    print("No unread emails found.")
else:
    # Process unread emails
    for i in email_ids:
        status, msg_data = mail.fetch(i, "(RFC822)")
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                
                sender = msg.get("From")
                sender_name = extract_name(sender)  # Extract only the name
                print(f"\nFrom: {sender_name}\nSubject: {subject}")

                # Extract email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # Summarize the email body
                if body.strip():
                    summary = summarize_text(body, num_sentences=2)
                    summary_text = f"{sender_name} says: {summary}"
                    print("Summary:", summary_text)
                    
                    # Read out the summary
                    read_summary(summary_text)
                else:
                    print("Email body is empty.")

# Close the connection
mail.logout()
