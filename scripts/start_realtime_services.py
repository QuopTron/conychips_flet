import subprocess
import time
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WS_SERVER = os.path.join(ROOT, 'tools', 'ws_server.py')
WS_CLIENT = os.path.join(ROOT, 'core', 'realtime', 'ws_client.py')

procs = []

def start():
    print('Starting WS broker...')
    p = subprocess.Popen(['python3', WS_SERVER], cwd=ROOT)
    procs.append(p)
    time.sleep(0.5)
    print('Starting WS client (background)...')
    p2 = subprocess.Popen(['python3', WS_CLIENT], cwd=ROOT)
    procs.append(p2)
    print('Started broker (pid=%s) and client (pid=%s)' % (p.pid, p2.pid))

if __name__ == '__main__':
    start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping processes...')
        for p in procs:
            p.terminate()
