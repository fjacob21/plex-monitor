#!/usr/bin/python3
import argparse
import docker
import requests
import paramiko
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import time
from configs import Configs


class Monitor(object):

    def __init__(self):
        super().__init__()
        self._configs = Configs()
    
    def send_email(self, dest, content, subject="Plex server SEV!!!", logs={}):
        src_email = self._configs.email
        server = "smtp.gmail.com"
        server_port = 587
        psw = self._configs.password

        fromaddr = src_email
        toaddr = dest
        msg = MIMEMultipart()
        msg['From'] = src_email
        msg['To'] = dest
        msg['Subject'] = subject
        msg.attach(MIMEText(content))
        if logs:
            log_content = ""
            for log in logs.items():
                log_content += f"{log[0]} - {log[1]}\n" 
                
            logsmsg = MIMEText(log_content, 'plain')
            logsmsg.add_header('Content-Disposition', 'attachment', filename='plex.log')
            msg.attach(logsmsg)

        try:
            server = smtplib.SMTP(server, server_port)
            server.starttls()
            server.login(fromaddr, psw)
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def get_logs(self, container):
        logs = {}
        for log in container.logs(timestamps=True).decode().strip().split("\n"):
            print(log)
            log = log.replace("\r", "")
            m = re.match(r"(\d*-\d*-\d*T\d*:\d*:\d*.\d*\w*) (.*)", log)
            timestamp = m.groups()[0]
            msg = m.groups()[1]
            if timestamp not in logs:
                logs[timestamp] = msg
        return logs

    def main(self):
        if self._configs.use_local_sock:
            client = docker.DockerClient(base_url="unix://var/run/docker.sock")
        elif self._configs.server:
            docker_service = f"ssh://{self._configs.user}@{self._configs.server}"
            client = docker.DockerClient(base_url=docker_service)
        else:
            client = docker.from_env()
        
        while True:
            c = client.containers.get('plex')
            start = c.attrs["State"]["StartedAt"]
            running = c.attrs["State"]["Running"]
            restarting = c.attrs["State"]["Restarting"]
            oomKilled = c.attrs["State"]["OOMKilled"]
            dead = c.attrs["State"]["Dead"]
            pid = c.attrs["State"]["Pid"]
            restart_count = c.attrs["RestartCount"]
            plex_html = False
            try:
                r = requests.get(f"http://{self._configs.server}:32400/web/index.html")
                if r.ok:
                    plex_html = True
            except Exception:
                plex_html = False
            if restarting or oomKilled or dead or not plex_html:
                print("Plex is not working", restarting, oomKilled, dead ,plex_html)
                # logs = get_logs(c)
                # send_email(self._configs.oncall, "Plex server not healty!", logs=logs)
            else:
                print("All is ok")
            time.sleep(1)






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor the plex server Docker container')
    # parser.add_argument('-c', '--container', metavar='container', default='plex', nargs='?',
    #                     help='The container name of the plex server')
    # parser.add_argument('-s', '--server', metavar='server', default='picluster1-pimaster', nargs='?',
    #                     help='The server to use')
    # parser.add_argument('-u', '--user', metavar='user', default='pi', nargs='?',
    #                     help='The user to use to connect to server')
    # parser.add_argument('-o', '--oncall', metavar='oncall', default='fjacob21@hotmail.com', nargs='?',
    #                     help='The email of the on call user')

    # args = parser.parse_args()

    # if args.server:
    #     docker_service = f"ssh://{args.user}@{args.server}"
    #     client = docker.DockerClient(base_url=docker_service)
    # else:
    #     client = docker.from_env()
    
    # c = client.containers.get('plex')
    # start = c.attrs["State"]["StartedAt"]
    # running = c.attrs["State"]["Running"]
    # restarting = c.attrs["State"]["Restarting"]
    # oomKilled = c.attrs["State"]["OOMKilled"]
    # dead = c.attrs["State"]["Dead"]
    # pid = c.attrs["State"]["Pid"]
    # restart_count = c.attrs["RestartCount"]
    # plex_html = False
    # try:
    #     r = requests.get(f"http://{args.server}:32400/web/index.html")
    #     if r.ok:
    #         plex_html = True
    # except Exception:
    #     plex_html = False
    # if restarting or oomKilled or dead or not plex_html:
    #     logs = get_logs(c)
    #     send_email(args.oncall, "Plex server not healty!", logs=logs)
    # else:
    #     print("All is ok")
    m = Monitor()
    m.main()