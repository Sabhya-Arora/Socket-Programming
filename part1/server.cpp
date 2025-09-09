// server.cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cstring>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "parse_json.hpp"
#define BUFFER_SIZE 1024
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

    for (int i = 1; i < argc; i++) {
        string arg = argv[i];
        if (arg == "--config" && i + 1 < argc) {
            config_path = argv[++i]; // assume non-flag arg = config path
        }
    }

    Config config_file = parse_config(config_path);
    string HOST = config_file.server_ip;
    int PORT = config_file.server_port;
    string filename = config_file.filename;

    // Load words from file
    ifstream file(filename);

    string content;
    getline(file, content); // assume single line, comma-separated
    vector<string> words = split(content, ',');
    file.close();

    int server_fd, new_socket;
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Allow quick reuse of port
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(HOST.c_str());
    address.sin_port = htons(PORT);

    
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    cout << "Server listening on " << HOST << ":" << PORT << "\n";

    while (true) {
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen)) < 0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }

    // Handle one client until it closes connection
    while (true) {
        char buffer[BUFFER_SIZE] = {0};
        int valread = read(new_socket, buffer, BUFFER_SIZE);
        if (valread <= 0) {
            // client closed connection or error
            close(new_socket);
            break;
        }

        string request(buffer, valread);
        // cout << "Client request: " << request;

        // Parse "p,k"
        int p, k;
        char comma;
        stringstream ss(request);
        ss >> p >> comma >> k;

        string response = "";
        if (p >= (int)words.size()) {
            response += "EOF\n";
        } else {
            for (int i = 0; i < k && (p + i) < (int)words.size(); i++) {
                response += words[p + i];
                if (i < k - 1 && (p + i + 1) < (int)words.size()) {
                    response += ",";
                }
            }
            if (p + k > (int)words.size()) response += ",EOF";
            response += "\n";
        }

        send(new_socket, response.c_str(), response.size(), 0);
    }
}


    return 0;
}