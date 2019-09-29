
run: venv
	. venv/bin/activate; python3 ./game.py

venv:
	python3 -m venv $@
	. venv/bin/activate; pip install pyglet
