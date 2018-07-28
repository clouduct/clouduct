SUPPORTED_SHELLS := bash zsh

completion_files := $(foreach shell_name, ${SUPPORTED_SHELLS}, completion/${shell_name}.complete)



.PHONY: dist completion prepare-dist clean lint

# create a shell completion file for a given shell (see SUPPORTED_SHELLS)
completion/%.complete: completion/
	_CLOUDUCT_BOOTSTRAP_COMPLETE=source-$* clouduct-bootstrap  > $@

clean:
	rm -rf completion
	rm -rf dist
	rm -rf .eggs
	rm -rf .cloduct-info

dist: clean prepare-dist
	poetry build

lint:
	flake8 clouduct

prepare-dist:  completion/ ${completion_files} lint

completion/:
	mkdir completion