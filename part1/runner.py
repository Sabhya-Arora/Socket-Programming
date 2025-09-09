# demo_runner.py
import json, os, time, pathlib
from topo_wordcount import make_net

cfg = json.loads(pathlib.Path("config.json").read_text())
p = cfg["p"]
k = cfg["k"]
print(f"Starting experiment with {p}, {k}")
net = make_net(); net.start()
h1, h2 = net.get('h1'), net.get('h2')

# start server with demo config
srv = h2.popen("./server --config config.json", shell=True, stdout = None, stderr = None)
time.sleep(0.5)

# run client once (no --quiet): prints word frequencies + ELAPSED_MS
print(h1.cmd(f"./client --config config.json --k {k}"))

srv.terminate(); time.sleep(0.2); net.stop()
print("Experiment completed")