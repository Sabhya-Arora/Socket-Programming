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
CLIENT_COUNTS = [1] + list(range(4, 33, 4))
RUNS_PER_COUNT = 5
SERVER_CMD = "python3 server.py --config config.json"
CLIENT_CMD_TMPL = "python3 client.py --config config.json"

RESULTS_CSV = Path("results.csv")


def modify_config(param: str, value, filename: str = "config.json"):
    with open(filename, "r") as f:
        config = json.load(f)
    config[param] = value
    with open(filename, "w") as f:
        json.dump(config, f, indent=2)


def run_experiment(num_clients: int, run_id: int, net, h_server, h_clients):
    """
    Runs a single experiment instance.
    - Starts the server and clients.
    - Captures and prints their stdout/stderr.
    - Records the completion time for each client.
    """
    print(f"\n--- Starting Run #{run_id} for {num_clients} clients ---")
    
    # Start server and capture its output streams
    print("Starting server...")
    srv = h_server.popen(SERVER_CMD, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)

    # Start all clients and capture their output streams
    print(f"Starting {num_clients} client(s)...")
    clients = []
    for cid, h_client in enumerate(h_clients, start=1):
        proc = h_client.popen(CLIENT_CMD_TMPL, shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        clients.append((cid, proc))

    elapsed = []
    # Wait for clients to finish and process their output
    for cid, proc in clients:
        out, err = proc.communicate()
        out = out.decode()
        err = err.decode()


        # Parse timing info
        m = re.search(r"ELAPSED_MS:(\d+)", out)
        if not m:
            print(f"[warn] No ELAPSED_MS for client={cid}, run={run_id}, nc={num_clients}.")
            continue
        ms = int(m.group(1))
        elapsed.append(ms)

        with RESULTS_CSV.open("a", newline="") as f:
            csv.writer(f).writerow([num_clients, run_id, cid, ms])

    print("\nStopping server...")


    srv.terminate()
    srv_out, srv_err = srv.communicate()
    srv_out = srv_out.decode()
    srv_err = srv_err.decode()

    return elapsed


def main():
    # Prepare CSV
    if RESULTS_CSV.exists():
        RESULTS_CSV.unlink() # Clear previous results
    with RESULTS_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["num_clients", "run", "client_id", "elapsed_ms"])

    for nc in CLIENT_COUNTS:
        print(f"\n================ Running with {nc} clients ================")

        net = make_net(num_clients=nc)
        net.start()

        h_server = net.get("server")
        h_clients = [net.get(f"c{i}") for i in range(1, nc + 1)]

        all_runs = []
        try:
            for r in range(1, RUNS_PER_COUNT + 1):
                modify_config("num_clients", nc)
                elapsed = run_experiment(nc, r, net, h_server, h_clients)
                if elapsed:
                    avg = sum(elapsed) / len(elapsed)
                    all_runs.append(avg)
                    print(f"\n> Run {r} Summary: avg {avg:.2f} ms over {len(elapsed)} clients")

            # summary per client count
            if all_runs:
                mean = statistics.mean(all_runs)
                stdev = statistics.stdev(all_runs) if len(all_runs) > 1 else 0
                print(f"\n[SUMMARY] {nc} clients: mean={mean:.2f}, stdev={stdev:.2f}")

        finally:
            net.stop()
    print("\nGenerating plot...")

    # Plot results
    xs, ys= [], []
    with RESULTS_CSV.open() as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            nc = int(row["num_clients"])
            ms = int(row["elapsed_ms"])
            data.setdefault(nc, []).append(ms)

        for nc in sorted(data):
            vals = data[nc]
            mean = statistics.mean(vals)
            if len(vals) > 1:
                stdev = statistics.stdev(vals)
            
            xs.append(nc)
            ys.append(mean)
    plt.plot(xs, ys, marker="o", label="Average Completion Time")   
    plt.xlabel("Number of Concurrent Clients")
    plt.ylabel("Average Completion Time per Client (ms)")
    plt.title("Completion Time vs. Number of Clients")
    plt.grid(True)
    plt.xticks(CLIENT_COUNTS)
    plt.legend()
    plt.tight_layout()

    plot_filename = "p2_plot.png"
    plt.savefig(plot_filename)
    print(f"Plot saved to {plot_filename}")
    plt.show()
        


if __name__ == "__main__":
    main()