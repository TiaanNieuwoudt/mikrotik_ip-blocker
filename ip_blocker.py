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

        connection = RouterOsApiPool(host=self.hostname, username=self.username, password=self.password,
                                     plaintext_login=True)
        return connection

########################################################################################################################

    def get_api(self):
        try:
            self.api = self.connection.get_api()

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

    def run_script(self, path, source, id):

        if not self.check_api():
            return None

        prefix = self.api.get_resource(path)
        prefix.add(name=id, source=source)

        self.api.get_resource(path).call('run', {'id': id})

        prefix.remove(id=id)

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
                regex_string = "Modify your set of IP's"
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

    def create_address_list(self, attempts):

        COMMAND_PATH = '/sys/script/'
        COMMAND_ID = 'ip_block'
        COMMAND_SOURCE = str()

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
                    COMMAND_SOURCE = COMMAND_SOURCE + '/ip firewall address-list add address={} list=BLOCKED_SUBNETS ' \
                                                      'timeout=36d\n'.format(ip)

                    ip_inst = BlockedIP(ip, datetime.datetime.now())
                    IPs.insert_IP(ip_address=ip_inst.IP, date_time=ip_inst.date_time)

            self.run_script(path=COMMAND_PATH, source=COMMAND_SOURCE, id=COMMAND_ID)

        self.connection.disconnect()

########################################################################################################################

    def full_sequence(self):
        self.connect()

        if not self.check_api():
            return None

        self.connection.get_api()
        log = self.check_log()
        self.create_address_list(log)


api_instance = API(hostname='10.253.254.1', username=your username, password=Your password)
