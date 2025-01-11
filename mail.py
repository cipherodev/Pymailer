import smtplib, imaplib, email
from email.message import EmailMessage

def load(file_path) -> list:
    """Return data"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, Exception):
        return []
        
class Emailer:
    """
    Sends and reads emails through Gmail.
    """
    def __init__(self, EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER = 'imap.gmail.com', SMTP_SERVER = 'smtp.gmail.com', IMAP_PORT = 993, SMTP_PORT = 587, allowed_emails_path = 'allowed_emails.json', saved_emails_path='saved_emails.json'):
        self.EMAIL_ADDRESS = EMAIL_ADDRESS
        self.EMAIL_PASSWORD = EMAIL_PASSWORD
        self.IMAP_SERVER = IMAP_SERVER
        self.SMTP_SERVER = SMTP_SERVER
        self.IMAP_PORT = IMAP_PORT
        self.SMTP_PORT = SMTP_PORT
        self.allowed_emails_path = [allowed_emails_path]
        self.saved_emails_path = saved_emails_path

        self.allowed_emails = load(self.allowed_emails_path)
        self.saved_emails = load(self.saved_emails_path)

        self.smtp = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
        self.imap = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)

        try:
            self.smtp.starttls()
            self.smtp.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
            self.imap.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)

        except Exception as e:
            print(f'Error logging in: {e}')
        self.imap.select('INBOX')
        

    def send(self, recipient, subject='', body='', images=None):
        """
        Sends a email to the recipient's email address, Ex: recipient@gmail.com 
        The subject, body, and images are optional. Note: Images need the image path(s) 
        in a list format, Ex: ['image1.png', 'image2.png'] or ['image1.png']
        """
        email = EmailMessage()
        email.set_content(body)
        email['To'] = recipient
        email['Subject'] = subject
        email['From'] = self.EMAIL_ADDRESS

        if images:
            for image in images:
                try:
                    img_name = image.split('/')[-1] # Get the filename from the image path

                    with open(image, 'rb') as img:
                        img = img.read()
                        
                    email.add_attachment(
                        img,
                        maintype='image',
                        subtype=img_name.split('.')[-1],  
                        filename=img_name
                    )
                except Exception as e:
                    print(f'Error attaching image: {e}')

        try:
            self.smtp.send_message(email)
        except:
            try:
                self.smtp.starttls()
                self.smtp.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                self.smtp.send_message(email)
            except Exception as e:
                return f'Error sending email: {e}'
        finally:
            return f'Successfully sent email to: {recipient}'
        
    def read(self, amount=1, unread_only=True, allowed_emails=None, box='INBOX'):
        """
        Reads emails from the specified mailbox (default is INBOX).
        Fetches the specified amount of emails that are either unread or all emails if unread_only is False.
        Filters emails based on the allowed_emails list and extracts image attachments.
        """
        if allowed_emails is None:
            allowed_emails = self.allowed_emails

        if box != 'INBOX':
            self.imap.select(box)

        try:
            criteria = 'UNSEEN' if unread_only else 'ALL'
            status, messages = self.imap.search(None, criteria)

            if status != 'OK':
                return f"Error searching emails: {status}"

            email_ids = messages[0].split()
            if not email_ids:
                return "No emails found."

            emails = []
            count = 0

            for email_id in email_ids[::-1]:  # Reverse to get latest emails first
                if count >= amount:
                    break

                # Fetch the email by ID
                status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    print(f"Error fetching email ID {email_id}")
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        sender = email.utils.parseaddr(msg['From'])[1]
                        subject = msg['Subject']
                        body = ""
                        images = []

                        if allowed_emails and sender not in allowed_emails:
                            continue

                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    body = part.get_payload(decode=True).decode()

                                if content_disposition and "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        content = part.get_payload(decode=True)
                                        images.append({
                                            'filename': filename,
                                            'content': content
                                        })
                        else:
                            body = msg.get_payload(decode=True).decode()

                        emails.append({
                            'from': sender,
                            'subject': subject,
                            'body': body,
                            'images': images
                        })
                        count += 1

            return emails

        except Exception as e:
            return f"Error reading emails: {e}"


            

            
