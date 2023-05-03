import os
import socket

from kubernetes import client


class Config:
    _K8SLOKILOGS_HOST_IP = "auto"
    _K8SLOKILOGS_HOST_PORT = 3100
    _K8SLOKILOGS_SCRAPER_SINCE_SECONDS = 60
    _K8SLOKILOGS_SCRAPER_NAMESPACE = "*"

    def __init__(self, k8s: client.CoreV1Api):
        self.K8SLOKILOGS_HOST_IP = os.getenv(
            "K8SLOKILOGS_HOST_IP", self._K8SLOKILOGS_HOST_IP
        )
        self.K8SLOKILOGS_HOST_PORT = int(
            os.getenv("K8SLOKILOGS_HOST_PORT", self._K8SLOKILOGS_HOST_PORT)
        )
        self.K8SLOKILOGS_SCRAPER_SINCE_SECONDS = os.getenv(
            "K8SLOKILOGS_SCRAPER_SINCE_SECONDS", self._K8SLOKILOGS_SCRAPER_SINCE_SECONDS
        )
        self.K8SLOKILOGS_SCRAPER_NAMESPACE = os.getenv(
            "K8SLOKILOGS_SCRAPER_NAMESPACE", self._K8SLOKILOGS_SCRAPER_NAMESPACE
        )

        namespaces = [n.metadata.name for n in k8s.list_namespace().items]
        if self.K8SLOKILOGS_SCRAPER_SINCE_SECONDS == "null":
            self.K8SLOKILOGS_SCRAPER_SINCE_SECONDS = None
        else:
            self.K8SLOKILOGS_SCRAPER_SINCE_SECONDS = int(
                self.K8SLOKILOGS_SCRAPER_SINCE_SECONDS
            )

        if (
            self.K8SLOKILOGS_SCRAPER_NAMESPACE not in namespaces
            and self.K8SLOKILOGS_SCRAPER_NAMESPACE != "*"
        ):
            raise ValueError(
                "Namespace %s not found in cluster context"
                % self.K8SLOKILOGS_SCRAPER_NAMESPACE
            )

        if self.K8SLOKILOGS_HOST_IP == "auto":
            self.K8SLOKILOGS_HOST_IP = Config.get_host_ipv4()

    @staticmethod
    def get_host_ipv4():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
