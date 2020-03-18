from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def mailer(to, message):
    # create message object instance
    msg = MIMEMultipart()

    message = message

    # setup the parameters of the message
    password = "Enter email password"
    msg['From'] = "enter sender address "
    msg['To'] = "enter receiver address"
    msg['Subject'] = "ip_blocker"

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # create server
    server = smtplib.SMTP('Enter smtp server with port number')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

    print("successfully sent email to %s:" % (msg['To']))
