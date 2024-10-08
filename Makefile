EXAMPLES := $(wildcard examples/*.txt)

.PHONY : examples $(EXAMPLES)

examples: $(EXAMPLES)

$(EXAMPLES):
	@echo
	@echo "#########"
	@echo "#" $@
	@echo "#########"
	@time --format="took %e sec" ./nonogram-solver.py $@

syntax:
	@python -m py_compile *.py
	@python -m py_compile nonogram/*.py

clean:
	@/usr/bin/find . -depth -type d -name '*__pycache__' -exec rm -rf {} \;

test:
	@python -m unittest discover

format:
	@python -m black nonogram-solver.py nonogram tests

