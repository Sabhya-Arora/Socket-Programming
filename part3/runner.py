# demo_runner.py
import json, os, time, pathlib
from topo_wordcount import make_net

# load base config and override p
cfg_path = pathlib.Path("config.json")
cfg = json.loads(cfg_path.read_text())

CLIENT_CMD_TMPL = f"python3 client.py --config {cfg_path}"
GREEDY_CLIENT_CMD_TMPL = f"python3 client.py --config {cfg_path} --greedy"
num_clients = cfg.get("num_clients", 1)
K = cfg.get("k", 1)
P = cfg.get("p", 0)
# build topology with num_clients
net = make_net(num_clients=num_clients)
net.start()

server = net.get("server")
clients = [net.get(f"c{i}") for i in range(1, num_clients + 1)]

srv = server.popen(
    f"python3 -u server.py --config {cfg_path}",
    shell=True,
    stdout=None,
    stderr=None
)

time.sleep(2)


def run_client(c, cfg_path, K, cmd):
    return c.popen(cmd, shell=True,
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
