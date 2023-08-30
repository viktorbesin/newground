SETUP_FILE = setup.py
APPLICATION_NAME = hybrid_grounding


compile:
	pip uninstall $(APPLICATION_NAME) -y
	python $(SETUP_FILE) install

clean:
	pip uninstall $(APPLICATION_NAME) -y

format:
	pylint hybrid_grounding


