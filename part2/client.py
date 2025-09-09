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
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = json.load(f)

    SERVER_IP = config["server_ip"]
    SERVER_PORT = config["server_port"]
    k = config["k"]
    # 'p' will be managed by the loop's range

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Record start time
    start = time.time()
    
    all_words = []
    incoming_buffer = b""

    for p in range(0, 10_000_000, k):
        msg = f"{p},{k}\n"
        try:
            sock.sendall(msg.encode())
        except socket.error as e:
            print(f"Failed to send data: {e}")
            break

        # Keep processing all complete requests by this client
        while b"\n" not in incoming_buffer:
            try:
                part = sock.recv(BUFFER_SIZE)
                incoming_buffer += part
            except socket.error as e:
                print(f"Error receiving data: {e}")
                break
        
        # Extract the first complete line from the buffer, keeping the rest
        line_bytes, _, incoming_buffer = incoming_buffer.partition(b"\n")
        line = line_bytes.decode().strip()

        #print(f"Server response partial: {line[:70]}...") # Print a snippet

        if "EOF" in line:
            final_words = [w.strip() for w in line.split(',') if w.strip() and 'EOF' not in w]
            all_words.extend(final_words)
            break
        
        # Process and store the words from the current line
        current_words = [w.strip() for w in line.split(',') if w.strip()]
        all_words.extend(current_words)

    # Record end time
    end = time.time()
    elapsed_ms = int((end - start) * 1000)
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

if __name__ == "__main__":
    main()
