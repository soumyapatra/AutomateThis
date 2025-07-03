#!/usr/bin/python3

import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender = 'alert@xxxxxxxxxxxxx'
receivers = ['xxxxxxxxxxxxx@xxxxxxxxx','xxxxxxxxxxxxxxx@xxxxxxxxxxxxxxx']



def sndmail(sender,receivers,sub):
        msg =MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receivers
        msg['Subject'] = "SMTP EXAMPLE"
        body = "This is test mail from Python"
        msg.attach(MIMEText(body,'plain'))
        message = f'From: {sender}\nTo: {receivers[0]}\n{sub}\n{body}'
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("xxxxxxxxxx@xxxxxxxxxx.com", "xxxxxxxxxxxxxxxxxx")
        txt=msg.as_string()
        server.sendmail(sender, receivers, txt)
        server.quit()
        print(msg,msg.as_string())
        print(type(msg))


sndmail(sender,receivers,"Python test Mail")
