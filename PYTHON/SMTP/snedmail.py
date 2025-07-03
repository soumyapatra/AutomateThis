#!/usr/bin/python3

import smtplib

sender = 'alert@xxxxxxxxx.com'
receivers = ['xxxxxxxxxx@xxxxxxxxx.com','xxxxxxxxx@xxxxxxxx.com']

message = """From: From Person <{}>
To: To Person <{}>
Subject: SMTP e-mail test

This is a test e-mail message.
""".format(sender,receivers)

try:
   smtpObj = smtplib.SMTP('localhost')
   smtpObj.sendmail(sender, receivers, message)
   print("Successfully sent mail")
except Exception as e:
   print("Mail not send",e)
