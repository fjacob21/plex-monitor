#!/usr/bin/python3
import argparse
import docker
import requests
import paramiko
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import logging
from configs import Configs


class PlexMonitor(object):

    def __init__(self) -> None:
        super().__init__()
        self._configs = Configs()
        self._pid = 0
        self._start = ""
        self._restart_count = 0
    
    def send_oncall_email(self) -> None:
        msg = MIMEMultipart()
        msg['From'] = self._configs.email
        msg['To'] = self._configs.oncall
        msg['Subject'] = "Plex server not healty!"
        msg.attach(MIMEText("Plex server not healty!"))
        logsmsg = MIMEText(self.get_logs(), 'plain')
        logsmsg.add_header('Content-Disposition', 'attachment', filename='plex.log')
        msg.attach(logsmsg)

        try:
            server = smtplib.SMTP(self._configs.smtp_server, self._configs.smtp_port)
            server.starttls()
            server.login(self._configs.email, self._configs.password)
            text = msg.as_string()
            server.sendmail(self._configs.email, self._configs.oncall, text)
            server.quit()
            return True
        except Exception as e:
            logging.exception(e)
            return False
    
    def get_logs(self):
        container = self._client.containers.get('plex')
        log_content = ""
        for log in container.logs(timestamps=True).decode().strip().split("\n"):
            log = log.replace("\r", "")
            m = re.match(r"(\d*-\d*-\d*T\d*:\d*:\d*.\d*\w*) (.*)", log)
            timestamp = m.groups()[0]
            msg = m.groups()[1]
            log_content += f"{timestamp} - {msg}\n" 
        return log_content

    def setup_docker_client(self):
        try:
            if self._configs.use_local_sock:
                self._client = docker.DockerClient(base_url="unix://var/run/docker.sock")
            elif self._configs.server:
                docker_service = f"ssh://{self._configs.user}@{self._configs.server}"
                self._client = docker.DockerClient(base_url=docker_service)
            else:
                self._client = docker.from_env()
            return True
        except Exception as e:
            logging.exception("Cannot create Docker client", e)
            self._client = None
            return False

    @property
    def is_container_healthy(self) -> bool:
        container = self._client.containers.get('plex')
        start = container.attrs["State"]["StartedAt"]
        pid = container.attrs["State"]["Pid"]
        restart_count = container.attrs["RestartCount"]
        running = container.attrs["State"]["Running"]
        restarting = container.attrs["State"]["Restarting"]
        oomKilled = container.attrs["State"]["OOMKilled"]
        dead = container.attrs["State"]["Dead"]
        
        if self._pid == 0:
            self._pid = pid
            self._start = start
            self._restart_count = restart_count
        if (
            self._pid != pid
            or self._start != start
            or self._restart_count != restart_count
            or restarting
            or oomKilled
            or dead
        ):
            self._pid = pid
            self._start = start
            self._restart_count = restart_count
            return False
        return True

    @property
    def is_server_healthy(self) -> bool:
        try:
            r = requests.get(f"http://{self._configs.server}:32400/web/index.html")
            if r.ok:
                return True
        except Exception:
            return False
    
    @property
    def is_plex_healthy(self) -> bool:
        return self.is_container_healthy and self.is_server_healthy

    def main(self):
        
        if not self.setup_docker_client():
            return 1
        while True:
            if self.is_plex_healthy:
                logging.error("Plex is not healthy")
                self.send_oncall_email()
            else:
                logging.debug("All is ok")
            time.sleep(self._configs.cycle)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor the plex server Docker container')
    parser.parse_args()
    m = PlexMonitor()
    m.main()