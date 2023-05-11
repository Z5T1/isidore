# Misc variables
VERSION=0.1.1
PYTHON=python3

# Sources
SOURCES=src/isidore README.md LICENSE pyproject.toml

# Generated files
PY_WHL_PKG=dist/isidore-$(VERSION)-py3-none-any.whl
PY_SRC_PKG=dist/isidore-$(VERSION).tar.gz 

$(PY_SRC_PKG) $(PY_WHL_PKG): $(SOURCES) | dist
	$(PYTHON) -m build

dist:
	mkdir dist

install: $(PY_WHL_PKG)
	$(PYTHON) -m pip install --ignore-installed $(PY_WHL_PKG)

clean:
	rm -rf dist

.PHONY: clean

