syntax:
	python -m py_compile *.py
	python -m py_compile nonogram/*.py

clean:
	rm -f *.pyo *.pyc
