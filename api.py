import socket
import pickle
from ip_db import IPs
import datetime
from email_sender import mailer
import schedule

today = datetime.datetime.now().strftime("%d-%m-%y")

from ip_blocker import timer


def db_insert():
    s = socket.socket()
    host = socket.gethostname()
    port = 8080
    s.bind((host, port))

    s.listen(5)

    while True:
        c, addr = s.accept()
        print("got connection from", addr)
        data = c.recv(4096)
        print(data)
        obj = pickle.loads(data)
        print(obj)

        for ip in obj:
            IPs.insert_IP(ip.IP, ip.date_time)


def today_report():
    list_of_today = list()
    message = ""
    today_ips = IPs.query_date()
    if len(today_ips) != 0:
        for ip_date in today_ips:
            if ip_date.date_time[0:8] == today:
                list_of_today.append(ip_date)

    if len(list_of_today) != 0:
        for ip in list_of_today:
            message =  message + str(ip.ip_address) + '  Blocked at:  ' + str(ip.date_time) + '\n'

        mailer('tiaan.n@twk.co.za', message)


def scheduler():
    schedule.every(1).minutes.do(timer)
    schedule.every().day.at("20:59").do(today_report)
    while True:
        schedule.run_pending()

scheduler()