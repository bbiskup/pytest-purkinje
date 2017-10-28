update:
	pip install -r dev-requirements.txt
	pip install -e .

upload-pypi:
	python setup.py sdist upload -r pypi

