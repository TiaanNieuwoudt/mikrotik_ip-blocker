from routeros_api import RouterOsApiPool
from routeros_api.exceptions import RouterOsApiConnectionError
import re
import datetime
from ip_db import IPs


class BlockedIP:

    def __init__(self, ip, date_time):
        self.IP = ip
        self.date_time = date_time


########################################################################################################################


class API:
    def __init__(self, hostname, username, password):

        # Router Credentials
        self.hostname = hostname
        self.username = username
        self.password = password

        self.connection = None

        self.api = None

    ########################################################################################################################

    def connect(self):

        self.connection = RouterOsApiPool(host=self.hostname, username=self.username, password=self.password,
                                     plaintext_login=True)
        return self.connection

    ########################################################################################################################

    def get_api(self):
        try:
            self.api = self.connection.get_api()
            return self.api
        except RouterOsApiConnectionError:
            self.api = None

    ########################################################################################################################

    def check_api(self):
        if self.api:
            try:
                self.api.get_resource('log').get()
                return self.api

            except RouterOsApiConnectionError:
                self.api = None
                return self.api

    ########################################################################################################################

    def add_ips(self, address, list):

        if not self.check_api():
            return None

        prefix = self.api.get_resource('ip/firewall/address-list')
        prefix.add(address=address, list=list, timeout='35d')



    ########################################################################################################################

    def check_log(self):

        if not self.check_api():
            print("Failed attemtps could not create API instance, finnishing up script")
            return None

        logged_attempts = list()
        saved_attempts = list()
        log = self.api.get_resource('log').get()

        for entry in log:
            if "denied winbox/dude connect from" in entry["message"]:
                ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", entry["message"])[0]

                logged_attempt = dict()
                logged_attempt["id"], logged_attempt["ip"] = entry["id"], ip
                regex_string = "Modify your IP specifications Here"
                white_list = re.findall(regex_string, ip)

                if not white_list:
                    logged_attempts.append(logged_attempt)

        if len(saved_attempts) > 0:
            for saved_attempt in saved_attempts:
                if len(logged_attempts) > 0:
                    for logged_attempt in logged_attempts:
                        if saved_attempt["id"] != logged_attempt["id"]:
                            saved_attempts.append(logged_attempt)

        else:
            for logged_attempt in logged_attempts:
                saved_attempts.append(logged_attempt)

        return saved_attempts

    ########################################################################################################################

    def attempt_counter(self, attempts):

        if attempts:
            ip_counter = list()
            tested_ips = list()

            for attempt in attempts:
                attempt_ip = attempt["ip"]
                if len(ip_counter) > 0:
                    if attempt_ip not in tested_ips:
                        new_counter = dict()
                        new_counter["ip"], new_counter["counter"] = attempt_ip, 1

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

        ip_counter = None
        return ip_counter

########################################################################################################################
########################################################################################################################

    def create_address_list(self, attempts):

        COMMAND_PATH = '/sys/script/'
        COMMAND_ID = 'ip_block'


        exsisting_ips = list()

        if not self.check_api():
            print("Error connecting to API while creating starting address list")
            return None

        if not attempts:
            return None

        blocked_subnet = self.api.get_resource('/ip/firewall/address-list').get()
        for subnet in blocked_subnet:
            if subnet["list"] == "BLOCKED_SUBNETS":
                exsisting_ips.append(subnet["address"])

        if attempts:
            for attempt in attempts:
                ip = attempt["ip"]
                if ip not in exsisting_ips:
                    print(ip)
                    self.add_ips(address=ip, list="BLOCKED_SUBNETS")

                    ip_inst = BlockedIP(ip, datetime.datetime.now())
                    IPs.insert_IP(ip_address=ip_inst.IP, date_time=ip_inst.date_time)

        self.connection.disconnect()

########################################################################################################################

    def full_sequence(self):
        self.connect()

        self.get_api()
        print(self.api)

        if not self.check_api():
            return None

        log = self.check_log()
        attempt_counter = self.attempt_counter(log)
        self.create_address_list(attempt_counter)


api_instance = API(hostname='1.1.1.1', username=Your username, password= Your password)
