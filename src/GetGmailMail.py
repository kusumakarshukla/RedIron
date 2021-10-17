# %load GetGmailMail.py
import os
import pickle
from typing import final
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
import base64
from bs4 import BeautifulSoup
import lxml
import html5lib 

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
class ReadGmail:

        def __init__(self,email):
            self.email_id = email
            self.service = self.gmail_authenticate()

        def gmail_authenticate(self):

                    flow = InstalledAppFlow.from_client_secrets_file('config/gmailpython.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    return build('gmail', 'v1', credentials=creds)

        def parse_parts(self, parts, folder_name, message):
            """
            Utility function that parses the content of an email partition
            """
            
            if parts:
                for part in parts:
                    filename = part.get("filename")
                    mimeType = part.get("mimeType")
                    body = part.get("body")
                    data = body.get("data")
                    file_size = body.get("size")
                    part_headers = part.get("headers")
                    if part.get("parts"):
                        # recursively call this function when we see that a part
                        # has parts inside
                        self.parse_parts( part.get("parts"), folder_name, message)
                    if mimeType == "text/plain":
                        # if the email part is text plain
                        if data:
                            text = urlsafe_b64decode(data).decode()
                    elif mimeType == "text/html":
                        # if the email part is an HTML content
                        # save the HTML file and optionally open it in the browser
                        if not filename:
                            filename = "index.html"
                        filepath = os.path.join(folder_name, filename)
                        with open(filepath, "wb") as f:
                            f.write(urlsafe_b64decode(data))
                    else:
                        # attachment other than a plain text or HTML
                        for part_header in part_headers:
                            part_header_name = part_header.get("name")
                            part_header_value = part_header.get("value")
                            if part_header_name == "Content-Disposition":
                                if "attachment" in part_header_value:
                                    # we get the attachment ID 
                                    # and make another request to get the attachment itself
                                    print("Saving the file:", filename, "size:", self.get_size_format(file_size))
                                    attachment_id = body.get("attachmentId")
                                    attachment = self.service.users().messages() \
                                                .attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                                    data = attachment.get("data")
                                    filepath = os.path.join(folder_name, filename)
                                    if data:
                                        with open(filepath, "wb") as f:
                                            f.write(urlsafe_b64decode(data))
        def read_message(self, message):
            """
            This function takes Gmail API `service` and the given `message_id` and does the following:
                - Downloads the content of the email
                - Prints email basic information (To, From, Subject & Date) and plain/text parts
                - Creates a folder for each email based on the subject
                - Downloads text/html content (if available) and saves it under the folder created as index.html
                - Downloads any file that is attached to the email and saves it in the folder created
            """
            msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            # parts can be the message body, or attachments
            payload = msg['payload']
            message_content=msg['payload']['parts'][1]['body']['data']
            headers = payload.get("headers")
            if headers:
                # this section prints email basic info & creates a folder for the email
                for header in headers:
                    name = header.get("name")
                    value = header.get("value")
                    if name.lower() == 'from':
                        # we print the From address
                        print("From:", value)
                    if name.lower() == "to":
                        # we print the To address
                        print("To:", value)
                    if name.lower() == "subject":                        
                        print("Subject:", value)
                    if name.lower() == "date":
                        # we print the date when the message was sent
                        print("Date:", value)
            message_content = message_content.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(message_content)
            soup = BeautifulSoup(decoded_data , 'html.parser')
            final_mail = self.clean_mail(soup.text)
            return final_mail
            

        def clean_mail(self,text):
            content = text.split("\n")
            cleaned_content = '\n'.join(list(filter(lambda s:len(s)>1 and s!='\t',content)))
            return cleaned_content

        def search_messages(self, query):

                result = self.service.users().messages().list(userId='me',q=query).execute()
                
                messages = [ ]
                if 'messages' in result:
                    messages.extend(result['messages'])
                while 'nextPageToken' in result:
                    page_token = result['nextPageToken']
                    result = self.service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
                    if 'messages' in result:
                        messages.extend(result['messages'])                
                
                try:
                        mail = self.read_message(messages[0])
                        return mail
                except Exception as e:
                        print("Error occured during Email Parsing")
                
            
        def get_size_format(self,b, factor=1024, suffix="B"):
                """
                Scale bytes to its proper byte format
                e.g:
                    1253656 => '1.20MB'
                    1253656678 => '1.17GB'
                """
                for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
                    if b < factor:
                        return f"{b:.2f}{unit}{suffix}"
                    b /= factor
                return f"{b:.2f}Y{suffix}"

        def clean(self,text):
                # clean text for creating a folder
                return "".join(c if c.isalnum() else "_" for c in text)




