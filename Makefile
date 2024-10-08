EXAMPLES := $(wildcard examples/*.txt)
NIN_EXAMPLES := $(wildcard examples/FORMAT-NIN/*.nin)

.PHONY : examples $(EXAMPLES) $(NIN_EXAMPLES)

examples: $(EXAMPLES) $(NIN_EXAMPLES)

$(EXAMPLES):
	@echo
	@echo "#########"
	@echo "#" $@
	@echo "#########"
	@time --format="took %e sec" ./nonogram-solver.py $@

$(NIN_EXAMPLES):
	@echo
	@echo "#########"
	@echo "#" $@
	@echo "#########"
	@time --format="took %e sec" ./nonogram-solver.py --format-nin $@

syntax:
	@python -m py_compile *.py
	@python -m py_compile nonogram/*.py

clean:
	@/usr/bin/find . -depth -type d -name '*__pycache__' -exec rm -rf {} \;

test:
	@python -m unittest discover

format:
	@python -m black nonogram-solver.py nonogram tests

