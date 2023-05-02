from pathlib import Path
import subprocess

import toml


project_path = Path('.').parent.parent


def build():
    pyproject = toml.load(project_path / 'pyproject.toml')
    tags = [pyproject['tool']['poetry']['version']]
    docker_conf = pyproject['tool']['docker']['build']
    name = pyproject['tool']['poetry']['name']
    if docker_conf['use_latest']:
        tags.append('latest')
    for architecture in docker_conf['architectures']:
        for tag in tags:
            image_name = f'{docker_conf["registry"]}/{name}:{architecture}-{tag}'
            args = (
                'docker', 'build', '--platform', f'linux/{architecture}',
                '-t', image_name, str(project_path / 'Dockerfile'),
            )
            subprocess.call(args)
            print(f'Built {image_name}')


def push():
    pyproject = toml.load(project_path / 'pyproject.toml')
    tags = [pyproject['tool']['poetry']['version']]
    docker_conf = pyproject['tool']['docker']['build']
    name = pyproject['tool']['poetry']['name']
    if docker_conf['use_latest']:
        tags.append('latest')
    for architecture in docker_conf['architectures']:
        for tag in tags:
            image_name = f'{docker_conf["registry"]}/{name}:{architecture}-{tag}'
            args = (
                'docker', 'push', image_name,
            )
            subprocess.call(args)
            print(f'Pushed {image_name}')
