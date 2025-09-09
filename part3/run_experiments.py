#!/usr/bin/env python3
import re
import time
import csv
from pathlib import Path
from topo_wordcount import make_net
import json
import subprocess
import statistics
import matplotlib.pyplot as plt

# Config
GREEDY_PARALLEL = [i for i in range(1, 11)]
RUNS_PER_C = 5
CLIENTS = 10
SERVER_CMD = "python3 server.py --config config.json"
CLIENT_CMD_TMPL = "python3 client.py --config config.json"
GREEDY_CLIENT_CMD_TMPL = "python3 client.py --config config.json --greedy"

RESULTS_CSV = Path("results.csv")


def modify_config(param: str, value, filename: str = "config.json"):
    with open(filename, "r") as f:
        config = json.load(f)
    config[param] = value
    with open(filename, "w") as f:
        json.dump(config, f, indent=2)


def run_experiment(c, run_id: int, h_server, h_clients):
    print(f"\n--- Starting Run #{run_id} for {c} requests by rogue client ---")
    
    srv = h_server.popen(SERVER_CMD, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)

    clients = []
    for cid, h_client in enumerate(h_clients, start=1):
        if cid == 10:  # greedy
            proc = h_client.popen(GREEDY_CLIENT_CMD_TMPL, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            proc = h_client.popen(CLIENT_CMD_TMPL, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        clients.append((cid, proc))

    greedy_time = None
    normal_times = []

    for cid, proc in clients:
        out, err = proc.communicate()
        out, err = out.decode(), err.decode()

        m = re.search(r"ELAPSED_MS:(\d+)", out)
        if not m:
            print(f"[warn] No ELAPSED_MS for client={cid}, run={run_id}, C={c}.")
            continue
        ms = int(m.group(1))

        if cid == 10:
            greedy_time = ms
        else:
            normal_times.append(ms)

        with RESULTS_CSV.open("a", newline="") as f:
            csv.writer(f).writerow([c, run_id, cid, ms])

    srv.terminate()
    srv_out, srv_err = srv.communicate()
    return greedy_time, normal_times



def main():
    if RESULTS_CSV.exists():
        RESULTS_CSV.unlink()
    with RESULTS_CSV.open("w", newline="") as f:
        csv.writer(f).writerow(["c", "run", "client_id", "elapsed_ms"])

    jfi_results = []

    for c in GREEDY_PARALLEL:
        print(f"\n================ {c} requests by the greedy client ================")

        net = make_net(num_clients=CLIENTS)
        net.start()

        h_server = net.get("server")
        h_clients = [net.get(f"c{i}") for i in range(1, CLIENTS + 1)]

        greedy_runs = []
        normal_runs = []

        try:
            for r in range(1, RUNS_PER_C + 1):
                modify_config("c", c)
                greedy_time, normal_times = run_experiment(c, r, h_server, h_clients)

                if greedy_time and normal_times:
                    greedy_runs.append(greedy_time)
                    normal_runs.append(normal_times)

            if greedy_runs and normal_runs:
                greedy_avg = statistics.mean(greedy_runs)
                normal_avg = [statistics.mean(times) for times in zip(*normal_runs)]

                # Jain’s Fairness Index
                x_greedy = 1 / greedy_avg
                xs = [x_greedy] + [1 / x for x in normal_avg]

                jfi = (sum(xs) ** 2) / (len(xs) * sum(x * x for x in xs))
                jfi_results.append((c, jfi))

                print(f"[SUMMARY] c={c}: Greedy avg={greedy_avg:.2f} ms, Normal avgs={normal_avg} ms, JFI={jfi:.4f}")

        finally:
            net.stop()

    # Plot JFI vs c
    if jfi_results:
        cs, jfis = zip(*jfi_results)
        plt.plot(cs, jfis, marker="o")
        plt.xlabel("Greedy Client Requests (c)")
        plt.ylabel("Jain's Fairness Index (JFI)")
        plt.title("JFI vs Greedy Client Requests")
        plt.grid(True)
        plt.savefig("p3_plot.png")
        plt.show()


main()