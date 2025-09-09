#include <bits/stdc++.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <chrono>
using namespace std;
#define BUFFER_SIZE 1024
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <stdexcept>
#include <algorithm>
#include "parse_json.hpp"
using namespace std;



vector<string> split(const string &str, char delimiter) {
    vector<string> tokens;
    stringstream ss(str);
    string token;
    while (getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

int main(int argc, char* argv[]) {
    string config_path = "config.json";
    int k;
    int cmd_k = -1;
    for (int i = 1; i < argc; i++) {
        string arg = argv[i];
        if (arg == "--k" && i + 1 < argc) {
            cmd_k = std::stoi(argv[++i]);
        } else if (arg == "--config" && i + 1 < argc) {
            config_path = argv[++i]; // assume non-flag arg = config path
        }
    }
    
    Config config_file = parse_config(config_path);

    string SERVER_IP = config_file.server_ip;
    int SERVER_PORT = config_file.server_port;
    k = config_file.k;
    if (cmd_k > 0) k = cmd_k;
    int p = config_file.p;

    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        cerr << "Socket creation error\n";
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERVER_PORT);
    // cout<<SERVER_PORT<<" "<<SERVER_IP<<" "<<k<<" "<<p<<endl;
    
    if (inet_pton(AF_INET, SERVER_IP.c_str(), &serv_addr.sin_addr) <= 0) {
        cerr << "Invalid address / Address not supported\n";
        return -1;
    }
    
    // record start time
    auto start = chrono::steady_clock::now();

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        cerr << "Connection Failed\n";
        return -1;
    }
    char buffer[BUFFER_SIZE];
    string response;
    int lengthread = 0;

    for (;; p += k) {
        stringstream msg;
        msg << p << "," << k << "\n";
        send(sock, msg.str().c_str(), msg.str().size(), 0);

        memset(buffer, 0, BUFFER_SIZE);
        int valread = read(sock, buffer, BUFFER_SIZE - 1);
        
        string chunk(buffer, valread);
        chunk[chunk.size() - 1] = ',';
        response += chunk;

        // check if EOF token is present
        if (response.find("EOF") != string::npos) {
            break;
        }
    }


    // record end time
    auto end = chrono::steady_clock::now();
    auto elapsed_ms = chrono::duration_cast<chrono::milliseconds>(end - start).count();

    
    cout << "Server response: " << response;

    // Count frequencies
    map<string,int> freq;
    auto words = split(response, ',');
    for (auto &w : words) {
        if (w == "EOF\n" || w == "EOF") continue;
        if (!w.empty() && w.back() == '\n') w.pop_back();
        if (!w.empty()) freq[w]++;
    }


    cout << "Word frequencies:\n";
    for (auto &kv : freq) {
        cout << kv.first << ", " << kv.second << "\n";
    }

    cout << "ELAPSED_MS:" << elapsed_ms << "\n";

    close(sock);
    return 0;
}