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
    
    def load(self) -> None:
        with open(self._filename, "rt") as f:
            configs = json.load(f)
            self._container = configs["container"]
            self._server = configs["server"]
            self._user = configs["user"]
            self._use_local_sock = configs["use_local_sock"] == "True"
            self._smtp_server = configs["smtp_server"]
            self._smtp_port = int(configs["smtp_port"])
            self._email = configs["email"]
            self._password = configs["password"]
            self._oncall = configs["oncall"]
            self._cycle = float(configs["cycle"])
    
    @property
    def container(self) -> str:
        return self._container

    @property
    def server(self) -> str:
        return self._server
    
    @property
    def user(self) -> str:
        return self._user
    
    @property
    def use_local_sock(self) -> bool:
        return self._use_local_sock

    @property
    def smtp_server(self) -> str:
        return self._smtp_server
    
    @property
    def smtp_port(self) -> port:
        return self._smtp_port
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def password(self) -> str:
        return self._password
    
    @property
    def oncall(self) -> str:
        return self._oncall
    
    @property
    def cycle(self) -> float:
        return self._cycle