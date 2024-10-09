EXAMPLES := $(wildcard examples/*.nin)

.PHONY : examples $(EXAMPLES)

examples: $(EXAMPLES)

$(EXAMPLES):
	@echo
	@echo "#########"
	@echo "#" $@
	@echo "#########"
	@time --format="took %e sec" ./nonogram solve $@

syntax:
	@python -m py_compile nonogram
	@python -m py_compile nonogrampy/*.py

clean:
	@/usr/bin/find . -depth -type d -name '*__pycache__' -exec rm -rf {} \;

test:
	@python -m unittest discover

format:
	@python -m black nonogram nonogrampy

