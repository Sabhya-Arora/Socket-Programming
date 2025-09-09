PYTHON := python3

.PHONY: run plot clean

# Run one experiment with current config.json / demo_config.json
run-rr:
	@echo "Running single experiment..."
	sudo $(PYTHON) runner.py

# Run batch experiments and generate plot
plot: clean
	@echo "Running experiments (batch)..."
	sudo $(PYTHON) -u run_experiments.py

clean:
	rm -f results.csv plot.png
