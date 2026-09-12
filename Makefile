.PHONY: demo fault-demo rehab-demo rehab-fault-demo test verify clean

demo:
	PYTHONPATH=src python3 -m vector_mini.cli --scenario nominal --fast

fault-demo:
	PYTHONPATH=src python3 -m vector_mini.cli --scenario timeout --fast

rehab-demo:
	PYTHONPATH=src python3 -m vector_mini.rehab_cli --scenario nominal --csv demo_output/rehab.csv
	python3 tools/render_rehab.py demo_output/rehab.csv docs/assets/vector-mini-rehab.svg

rehab-fault-demo:
	PYTHONPATH=src python3 -m vector_mini.rehab_cli --scenario contact-fault

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

verify: test
	PYTHONPATH=src python3 -m vector_mini.cli --scenario nominal --fast --csv demo_output/nominal.csv
	PYTHONPATH=src python3 -m vector_mini.cli --scenario timeout --fast --csv demo_output/timeout.csv
	python3 tools/render_telemetry.py demo_output/nominal.csv demo_output/timeout.csv docs/assets/vector-mini-demo.svg
	PYTHONPATH=src python3 -m vector_mini.rehab_cli --scenario nominal --csv demo_output/rehab.csv
	PYTHONPATH=src python3 -m vector_mini.rehab_cli --scenario contact-fault --csv demo_output/rehab-contact-fault.csv
	python3 tools/render_rehab.py demo_output/rehab.csv docs/assets/vector-mini-rehab.svg

clean:
	rm -rf demo_output src/vector_mini/__pycache__ tests/__pycache__
