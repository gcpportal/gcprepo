'''
Created on Feb 8, 2019

@author: deepashree.kurnad
'''
import base64
from email.mime.text import MIMEText
from googleapiclient import discovery
import smtplib

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(http,user_id, message):
    from pprint import pprint

    from oauth2client.client import GoogleCredentials
            
    credentials = GoogleCredentials.get_application_default()
            
    service = discovery.build('gmail', 'v1', http=http)
    message = (service.users().messages().send(userId="me", body=message)
                   .execute())
    print 'Message Id: %s' % message['id']
    return message


def sendmailSMTP(message,to_address,sub):
        body = message
        message = MIMEText(body)
        message['Subject'] = sub 
        message['From'] = 'noreply@gcp.portal.com'
        message['To'] = to_address
 
        username = 'gcp.request.portal@gmail.com'  
        password = 'gcpportal.100'
        
        server = smtplib.SMTP('smtp.gmail.com', 25)  
        server.ehlo()
        server.starttls()
        server.login(username, password)  
        server.sendmail(message['From'], message['To'], message.as_string())  
        server.quit()
        
        
#     Functiion call for sending mail using "GMAIL API"
#             message=create_message(credentials_json["id_token"]["email"], "depakurnad97@gmail.com", "wishes", "Hey there!!")
#             send_message(http_auth,"depakurnad97@gmail.com", message) 

#    Function call for sending mail using SMTP server      