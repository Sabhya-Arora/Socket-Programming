PYTHON := python3

.PHONY: run plot clean

run:
	@echo "Running single experiment..."
	sudo $(PYTHON) runner.py

plot:
	@echo "Running experiments (batch) and making plot..."
	sudo $(PYTHON) run_experiments.py

clean:
	rm -f results.csv plot.png
