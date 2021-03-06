import os
import time
import subprocess
from sshtunnel import SSHTunnelForwarder
from proxstar.util import *
from flask import current_app as app


def start_websockify(websockify_path, target_file):
    result = subprocess.run(['pgrep', 'websockify'], stdout=subprocess.PIPE)
    if not result.stdout:
        subprocess.call(
            [
                websockify_path, '8081', '--token-plugin', 'TokenFile',
                '--token-source', target_file, '-D'
            ],
            stdout=subprocess.PIPE)


def stop_websockify():
    result = subprocess.run(['pgrep', 'websockify'], stdout=subprocess.PIPE)
    if result.stdout:
        pid = result.stdout.strip()
        subprocess.run(['kill', pid], stdout=subprocess.PIPE)
        time.sleep(3)
        if subprocess.run(
            ['pgrep', 'websockify'], stdout=subprocess.PIPE).stdout:
            time.sleep(10)
            if subprocess.run(
                ['pgrep', 'websockify'], stdout=subprocess.PIPE).stdout:
                print('Websockify didn\'t stop, killing forcefully.')
                subprocess.run(['kill', '-9', pid], stdout=subprocess.PIPE)


def get_vnc_targets():
    targets = []
    if os.path.exists(app.config['WEBSOCKIFY_TARGET_FILE']):
        target_file = open(app.config['WEBSOCKIFY_TARGET_FILE'])
        for line in target_file:
            target_dict = dict()
            values = line.strip().split(':')
            target_dict['token'] = values[0]
            target_dict['port'] = values[2]
            targets.append(target_dict)
        target_file.close()
    return targets


def add_vnc_target(port):
    targets = get_vnc_targets()
    target = next((target for target in targets if target['port'] == port),
                  None)
    if target:
        return target['token']
    else:
        target_file = open(app.config['WEBSOCKIFY_TARGET_FILE'], 'a')
        token = gen_password(32, 'abcdefghijklmnopqrstuvwxyz0123456789')
        target_file.write("{}: 127.0.0.1:{}\n".format(token, str(port)))
        target_file.close()
        return token


def delete_vnc_target(port):
    targets = get_vnc_targets()
    target = next((target for target in targets if target['port'] == port),
                  None)
    if target:
        targets.remove(target)
        target_file = open(app.config['WEBSOCKIFY_TARGET_FILE'], 'w')
        for target in targets:
            target_file.write("{}: 127.0.0.1:{}\n".format(
                target['token'], target['port']))
        target_file.close()


def start_ssh_tunnel(node, port):
    port = int(port)
    server = SSHTunnelForwarder(
        node,
        ssh_username='root',
        ssh_pkey='proxmox_ssh_key',
        remote_bind_address=('127.0.0.1', port),
        local_bind_address=('127.0.0.1', port))
    server.start()
    return server
