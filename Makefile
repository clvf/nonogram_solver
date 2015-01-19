syntax:
	python -m py_compile *.py
	python -m py_compile nonogram/*.py

clean:
	rm -f *.pyo *.pyc

autopep:
	autopep8 -ia *.py
	autopep8 -ia nonogram/*.py
	autopep8 -ia tests/*.py
