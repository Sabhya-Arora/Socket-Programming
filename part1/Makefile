CXX = g++
CXXFLAGS = -Wall -O2

SERVER = server
CLIENT = client
PYTHON = python3
all: build

build: $(SERVER) $(CLIENT)

$(SERVER): server.cpp parse_json.hpp
	$(CXX) $(CXXFLAGS) -o $(SERVER) server.cpp

$(CLIENT): client.cpp parse_json.hpp
	$(CXX) $(CXXFLAGS) -o $(CLIENT) client.cpp


run: build
	sudo $(PYTHON) runner.py


expt: build
	@echo "Running experiments (batch)..."
	sudo $(PYTHON) run_experiments.py

plot: results.csv
	@echo "Generating plot..."
	python3 plot_results.py

clean:
	rm -f $(SERVER) $(CLIENT)