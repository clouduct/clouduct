# clouduct

## Install development version to _use_ it

1. Clone the repository from https://github.com/clouduct/clouduct-bootstrap.git
2. Install Python 3
3. Install poetry (https://github.com/sdispater/poetry)
4. In the clouduct-bootstrap directory (<CBD>):
     - Invoke `make init`
     - Invoke `make dist`
5. Create a new directory somewhere else, for your new clouduct-based project
6. Create a virtualenv (Python 3!) and activate it
7. Invoke `pip install <CBD>/dist/clouduct-*-py3-none-any.whl`
8. Invoke `clouduct-bootstrap --templates-config file:<CBD>/clouduct-templates2.yaml --help`

## Install development version to hack on it
