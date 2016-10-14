init:
	pip install -r requirements.txt

test:
	python -m unittest discover

install_develop:
	python setup.py develop

install:
	python setup.py install
