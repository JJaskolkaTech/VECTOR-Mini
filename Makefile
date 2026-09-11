.PHONY: demo test verify clean

demo:
	PYTHONPATH=src python3 -m vector_mini.cli --scenario nominal --fast

fault-demo:
	PYTHONPATH=src python3 -m vector_mini.cli --scenario timeout --fast

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

verify: test
	PYTHONPATH=src python3 -m vector_mini.cli --scenario nominal --fast --csv demo_output/nominal.csv
	PYTHONPATH=src python3 -m vector_mini.cli --scenario timeout --fast --csv demo_output/timeout.csv
	python3 tools/render_telemetry.py demo_output/nominal.csv demo_output/timeout.csv docs/assets/vector-mini-demo.svg

clean:
	rm -rf demo_output src/vector_mini/__pycache__ tests/__pycache__
