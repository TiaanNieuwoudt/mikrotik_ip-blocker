from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def mailer(to, message):
    # create message object instance
    msg = MIMEMultipart()

    message = message

    # setup the parameters of the message
    password = "Z0~x*{I*xhDs"
    msg['From'] = "tiaan.n@twk.co.za"
    msg['To'] = "tiaan.n@twk.co.za"
    msg['Subject'] = "ip_blocker"

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # create server
    server = smtplib.SMTP('mail.twk.co.za: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

    print("successfully sent email to %s:" % (msg['To']))