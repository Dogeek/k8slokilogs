import os

from kubernetes import client, config
from kubernetes.client import exceptions

from k8slokilogs.config import Config
from k8slokilogs.loki import LokiClient


def get_containers(pod):
    containers = []
    containers.extend([c.name for c in pod.spec.init_containers or []])
    containers.extend([c.name for c in pod.spec.containers or []])
    return containers


def main():
    # Configs can be set in Configuration class directly or using helper utility
    if os.environ.get("K8SLOKILOGS_IN_ClUSTER", "true").lower() == "true":
        config.load_incluster_config()
    else:
        config.load_kube_config()
    v1 = client.CoreV1Api()
    env = Config(v1)
    loki = LokiClient(env)
    pods = (
        v1.list_pod_for_all_namespaces(watch=False)
        if env.K8SLOKILOGS_SCRAPER_NAMESPACE == "*"
        else v1.list_namespaced_pod(env.K8SLOKILOGS_SCRAPER_NAMESPACE, watch=False)
    )

    # Get logs for each pod in their respective namespaces
    for pod in pods.items:
        print("Logs for pod %s in namespace %s" % (pod.metadata.name, pod.metadata.namespace))
        containers = get_containers(pod)
        print("Containers: %s" % containers)
        for container in containers:
            print((
                f"v1.read_namespaced_pod_log('{pod.metadata.name}', "
                f"'{pod.metadata.namespace}', container='{container}', "
                "timestamps=True)"
            ))
            try:
                messages = v1.read_namespaced_pod_log(
                    pod.metadata.name, pod.metadata.namespace, container=container,
                    since_seconds=env.K8SLOKILOGS_SCRAPER_SINCE_SECONDS, timestamps=True,
                ).splitlines()
                loki.push(messages, pod, container)
            except exceptions.ApiException as e:
                print("Exception when calling CoreV1Api->read_namespaced_pod_log: %s" % e)
                continue
        loki.send()


if __name__ == "__main__":
    main()
