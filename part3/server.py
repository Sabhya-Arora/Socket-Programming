#!/usr/bin/env python3
import socket
import json
import types
import selectors

BUFFER_SIZE = 1024

def split(line, delimiter=','):
    return [tok.strip() for tok in line.split(delimiter) if tok.strip()]


def accept_conn(sock, sel):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = [addr, b"", b""]
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def handle_client(key, mask, words, sel):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
        except ConnectionError:
            recv_data = None # Treat connection reset as a closure

        if recv_data:
            data[1] += recv_data
            while b"\n" in data[1]:
                request, _, remaining = data[1].partition(b"\n")
                data[1] = remaining
                request = request.decode().strip()

                p_str, k_str = request.split(',')
                p, k = int(p_str), int(k_str)

                # Build response
                response_parts = []
                if p >= len(words):
                    response_parts.append("EOF")
                else:
                    end = min(p + k, len(words))
                    response_parts.extend(words[p:end])
                    if p + k >= len(words):
                        response_parts.append("EOF")

                resp_str = ",".join(response_parts) + "\n"
                data[2] += resp_str.encode()
        else:
            print(f"Closing connection to {data[0]}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data[2]:
            try:
                sent = sock.send(data[2])
                data[2] = data[2][sent:]
            except ConnectionError:
                print(f"Client {data[0]} disconnected, closing.")
                sel.unregister(sock)
                sock.close()

def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    HOST = config["server_ip"]
    PORT = config["server_port"]
    filename = config["filename"]

    with open(filename, "r") as f:
        content = f.readline().strip()
        words = split(content, ',')

    sel = selectors.DefaultSelector()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(32)
    server_socket.setblocking(False)
    sel.register(server_socket, selectors.EVENT_READ, data=None)
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_conn(key.fileobj, sel)
                else:
                    handle_client(key, mask, words, sel)
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server_socket.close()
        sel.close()

main()