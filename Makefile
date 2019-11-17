syntax:
	@python3.8 -m py_compile *.py
	@python3.8 -m py_compile nonogram/*.py

clean:
	@/usr/bin/find . -depth -type d -name '*__pycache__' -exec rm -rf {} \;

test:
	@python3.8 -m unittest discover
