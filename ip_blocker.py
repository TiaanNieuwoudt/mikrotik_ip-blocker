from routeros_api import RouterOsApiPool
import re
import datetime
import time
import socket
import pickle
from ip_db import IPs


class BlockedIP:
    def __init__(self, ip, date_time):
        self.IP = ip
        self.date_time = date_time


def socket_send(payload):
    pickled_payload = pickle.dumps(payload)
    s = socket.socket()
    host = socket.gethostname()
    port = 8080
    try:
        s.connect((host, port))
        s.sendall(pickled_payload)
        s.close()
    except ConnectionRefusedError:
        print("connection could not be made")


def api_connect(host, username, password, plaintext):
    connection = RouterOsApiPool(host=host, username=username, password=password, plaintext_login=plaintext)
    return connection


def failed_loggins(api):
    logged_attempts = list()
    saved_attempts = list()
    log = api.get_resource('log').get()

    for entry in log:

        if "denied winbox/dude connect from" in entry["message"]:
            ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", entry["message"])[0]

            logged_attempt = dict()
            logged_attempt["id"], logged_attempt["ip"] = entry["id"], ip

            white_list = re.findall(r"(160\.19\.23[2-5])\.", ip)

            print(white_list)
            if not white_list:
                logged_attempt["date_time"] = (datetime.date.today(), entry["time"])
                logged_attempts.append(logged_attempt)

    if len(saved_attempts) > 0:
        for saved_attempt in saved_attempts:
            if len(logged_attempts) > 0:
                for failed_attempt in logged_attempts:
                    if failed_attempt["id"] != saved_attempt["id"]:
                        saved_attempts.append(failed_attempt)

    else:
        for attempt in logged_attempts:
            saved_attempts.append(attempt)

    return saved_attempts


def attempt_counter(attempts):
    ip_counter = list()
    tested_ips = list()

    for attempt in attempts:
        attempt_ip = attempt["ip"]
        if len(ip_counter) > 0:
            if attempt_ip not in tested_ips:
                new_counter = dict()
                new_counter["ip"] = attempt_ip
                new_counter["counter"] = 1
                ip_counter.append(new_counter)
                tested_ips.append(new_counter["ip"])

            else:
                for ip_counter_entry in ip_counter:
                    if attempt_ip == ip_counter_entry["ip"]:
                        ip_counter_entry["counter"] += 1
        else:
            new_ip = dict()
            new_ip["ip"] = attempt_ip
            new_ip["counter"] = 1
            ip_counter.append(new_ip)
            tested_ips.append(new_ip["ip"])

    return ip_counter


def run_script(path, source, id, api):
    prefix = api.get_resource(path)
    prefix.add(name=id, source=source)
    api.get_resource(path).call('run', {'id': id})
    prefix.remove(id=id)


def create_address_list(api, attempts):
    exsisting_ips = list()
    new_ips = list()
    COMMAND_PATH = '/sys/script/'
    COMMAND_ID = 'ip_block'
    blocked_subnets = api.get_resource('/ip/firewall/address-list').get()

    for i in blocked_subnets:
        if i["list"] == "BLOCKED_SUBNETS":
            exsisting_ips.append(i["address"])

    print(len(attempts))
    for attempt in attempts:
        ip = attempt["ip"]
        if ip not in exsisting_ips:

            COMMAND_SOURCE = '/ip firewall address-list add address={} list=BLOCKED_SUBNETS timeout=36d'.format(ip)
            run_script(path=COMMAND_PATH, source=COMMAND_SOURCE, id=COMMAND_ID, api=api)
            ip_inst = BlockedIP(ip, datetime.datetime.now())
            IPs.insert_IP(ip_address=ip_inst.IP, date_time=ip_inst.date_time)


def timer():
    api = api_connect(host='10.253.254.1', username='TwK_C0r3', password='Ktm99O-F0ur-Str0k3',
                      plaintext=True)

    api_connection = api.get_api()
    logins = failed_loggins(api_connection)
    attempts = attempt_counter(logins)

    for attempt in attempts:
        print(attempt)

    create_address_list(api=api_connection, attempts=attempts)
    api.disconnect()


