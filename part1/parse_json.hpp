#include <string>
using namespace std;
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <stdexcept>
#include <algorithm>

struct Config {
    string server_ip;
    int server_port;
    int k;
    int p;
    string filename;
    int num_iterations;
};

// Helper: trim whitespace and quotes
string trim(const string &s) {
    size_t start = s.find_first_not_of(" \t\n\r\""); 
    size_t end   = s.find_last_not_of(" \t\n\r\"");
    if (start == string::npos || end == string::npos) return "";
    return s.substr(start, end - start + 1);
}

Config parse_config(const string &path) {
    ifstream file(path);
    if (!file.is_open()) {
        throw runtime_error("Could not open config file: " + path);
    }

    unordered_map<string,string> kv;
    string line;
    while (getline(file, line)) {
        // skip braces and empty lines
        if (line.find("{") != string::npos || line.find("}") != string::npos) continue;
        if (line.find(":") == string::npos) continue;

        // split on ':'
        string key, value;
        stringstream ss(line);
        getline(ss, key, ':');
        getline(ss, value, ',');

        key = trim(key);
        value = trim(value);
        kv[key] = value;
    }

    Config cfg;
    cfg.server_ip      = kv["server_ip"];
    cfg.server_port    = stoi(kv["server_port"]);
    cfg.k              = stoi(kv["k"]);
    cfg.p              = stoi(kv["p"]);
    cfg.filename       = kv["filename"];
    cfg.num_iterations = stoi(kv["num_iterations"]);
    return cfg;
}
