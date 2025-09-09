#!/usr/bin/env python3
import socket
import json
import argparse
import time
from collections import Counter

BUFFER_SIZE = 1024

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.json", help="Config file path")
    parser.add_argument("--greedy", action="store_true", help="Set true for greedy client")
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = json.load(f)

    SERVER_IP = config["server_ip"]
    SERVER_PORT = config["server_port"]
    k = config["k"]
    c = config.get("c", 1)
    if not args.greedy:
        c = 1
    # 'p' will be managed by the loop's range

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Record start time
    start = time.time()
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    
    all_words = []
    incoming_buffer = b""

    # Loop through offsets p to request chunks of words
    for p in range(0, 10_000_000, k*c):
        for i in range(c):
            msg = f"{p + i*k},{k}\n"
            try:
                sock.sendall(msg.encode())
            except socket.error as e:
                print(f"Failed to send data for request {i}: {e}")
                break
        # Keep receiving data until we have a full line in our buffer
        num_received = 0
        while num_received < c:
            try:
                part = sock.recv(BUFFER_SIZE)
                incoming_buffer += part
                #count \n in part
                num_received += part.count(b"\n")
            except socket.error as e:
                print(f"Error receiving data: {e}")
                break
        
        # while \n present in incoming buffer keep partiotning and adding in all words
        done = False
        while b"\n" in incoming_buffer:
            line_bytes, _, incoming_buffer = incoming_buffer.partition(b"\n")
            line = line_bytes.decode().strip()


            # Check for the End-Of-File marker to stop requesting
            if "EOF" in line:
                done = True
                # Process words from the final line, excluding the EOF marker
                final_words = [w.strip() for w in line.split(',') if w.strip() and 'EOF' not in w]
                all_words.extend(final_words)
                break
        
            # Process and store the words from the current line
            current_words = [w.strip() for w in line.split(',') if w.strip()]
            all_words.extend(current_words)
        if done:
            break

    # Record end time
    end = time.time()
    elapsed_ms = int((end - start) * 1000)
    # Get own IP
    local_ip = sock.getsockname()[0]

    print(f"\n[CLIENT {local_ip}] --- Download Complete ---")
    print(f"[CLIENT {local_ip}] Total words received: {len(all_words)}")

    
    # Count frequencies
    freq = Counter(all_words)

    print("\nWord frequencies:")

    for w, c in freq.items():
        print(f"{w}, {c}")


    print(f"ELAPSED_MS:{elapsed_ms}")

    sock.close()


main()