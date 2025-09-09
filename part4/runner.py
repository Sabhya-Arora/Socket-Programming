# demo_runner.py
import json, os, time, pathlib
import threading
from topo_wordcount import make_net
import subprocess

# load base config and override p
cfg_path = pathlib.Path("config.json")
cfg = json.loads(cfg_path.read_text())
SERVER_CMD = "python3 server.py --config config.json"
CLIENT_CMD_TMPL = "python3 client.py --config config.json"
GREEDY_CLIENT_CMD_TMPL = "python3 client.py --config config.json --greedy"
num_clients = cfg.get("num_clients", 10)
K = cfg.get("k", 1)
P = cfg.get("p", 0)
# build topology with num_clients
net = make_net(num_clients=num_clients)
net.start()

server = net.get("server")
clients = [net.get(f"c{i}") for i in range(1, num_clients + 1)]

srv = server.popen(
    SERVER_CMD,
    shell=True,
    stdout=None,
    stderr=None
)

 # non blocking



def run_client(c, cfg_path, K, command):
    return c.popen(command, shell=True,
            stdout=None, stderr=None)  # inherit parent terminal

clproc = []
for id, c in enumerate(clients):
    if id == 0:
        clproc.append(run_client(c, cfg_path, K, GREEDY_CLIENT_CMD_TMPL))
    else:
        clproc.append(run_client(c, cfg_path, K, CLIENT_CMD_TMPL))
    
for cl in clproc:
    cl.wait()

srv.terminate()
srv.wait()
time.sleep(0.2)
net.stop()
