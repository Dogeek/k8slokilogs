from collections import defaultdict
import json
import platform

import requests

from k8slokilogs.models import Message
from k8slokilogs.config import Config


class LokiClient:
    def __init__(self, conf: Config):
        self.url = f"http://{conf.K8SLOKILOGS_HOST_IP}:{conf.K8SLOKILOGS_HOST_PORT}/api/prom/push"
        self.session = requests.session()
        self.session.headers["Content-Type"] = "application/json"
        self.entries = defaultdict(list)

    def parse_message(self, message: str) -> Message:
        ts, line = message.split(" ", 1)
        return Message(ts, line)

    def format_labels(self, labels: str) -> str:
        labels: dict = json.loads(labels)
        labels.update(
            {
                "node_architecture": platform.machine(),
                "node_version": platform.version(),
                "node_platform": platform.platform(),
                "node_system": platform.system(),
                "node_uname": " ".join(platform.uname()),
                "node_processor": platform.processor(),
            }
        )
        array = []
        for name, value in labels.items():
            array.append(f'{name}=\\"{value}\\"')
        return f"{{{','.join(array)}}}"

    def push(self, messages: list[str], pod, container_name: str):
        labels = json.dumps(
            {
                "namespace": pod.metadata.namespace,
                "pod_name": pod.metadata.name,
                "container_name": container_name,
            }
        )
        messages: list[Message] = [self.parse_message(message) for message in messages]
        self.entries[labels].extend(
            [
                {
                    "ts": message.ts,
                    "line": message.line,
                }
                for message in messages
            ]
        )

    def send(self):
        print("Sending to Loki...")
        print("%s labels" % len(self.entries))
        for labels, entries in self.entries.items():
            lbl = json.loads(labels)
            fmt = f"{lbl['namespace']}/{lbl['pod_name']}/{lbl['container_name']}"
            print(self.format_labels(labels))
            print("%s entries for namespace/pod/container %s" % (len(entries), fmt))

        streams = [
            {
                "labels": self.format_labels(labels),
                "entries": entries,
            }
            for labels, entries in self.entries.items()
        ]
        payload = {
            "streams": streams,
        }
        response = self.session.post(self.url, data=json.dumps(payload))
        print("loki: ", response.text)
        self.entries = defaultdict(list)
