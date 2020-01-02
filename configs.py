import json


class Configs(object):

    def __init__(self, filename="configs.json"):
        super().__init__()
        self._filename = filename
        self._container = ""
        self._use_local_sock = False
        self._server = ""
        self._user = ""
        self._email = ""
        self._password = ""
        self._oncall = ""
        self.load()
    
    def load(self):
        with open(self._filename, "rt") as f:
            configs = json.load(f)
            self._container = configs["container"]
            self._server = configs["server"]
            self._use_local_sock = configs["use_local_sock"] == "True"
            self._user = configs["user"]
            self._email = configs["email"]
            self._password = configs["password"]
            self._oncall = configs["oncall"]
    
    @property
    def container(self):
        return self._container

    @property
    def server(self):
        return self._server
    
    @property
    def use_local_sock(self):
        return self._use_local_sock

    @property
    def user(self):
        return self._user
    
    @property
    def email(self):
        return self._email
    
    @property
    def password(self):
        return self._password
    
    @property
    def oncall(self):
        return self._oncall