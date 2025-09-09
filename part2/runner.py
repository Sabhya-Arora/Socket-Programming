# runner.py
import json, os, time, pathlib
from topo_wordcount import make_net

# load base config and override p
cfg_path = pathlib.Path("config.json")
cfg = json.loads(cfg_path.read_text())

num_clients = cfg.get("num_clients", 1)
K = cfg.get("k", 1)
P = cfg.get("p", 0)

print(f"Starting experiment with number of clients = {num_clients}")
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


def run_client(c, cfg_path, K):
    return c.popen(f"python3 -u client.py --config {cfg_path}", shell=True,
            stdout=None, stderr=None)  # inherit parent terminal

clproc = []
for c in clients:
    clproc.append(run_client(c, cfg_path, K))
    
for cl in clproc:
    cl.wait()

srv.terminate()
srv.wait()
time.sleep(0.2)
net.stop()

print("Experiment completed")