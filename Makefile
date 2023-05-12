DESTDIR=/opt/isidore
BINDIR=$(DESTDIR)/bin
DOCDIR=$(DESTDIR)/share/doc/isidore

.PHONY: install install-bin install-doc all clean

all:
	$(MAKE) -C lib

clean:
	$(MAKE) -C lib clean

install: install-bin install-doc install-lib

install-bin:
	mkdir -p "$(BINDIR)"
	cp -r bin/* "$(BINDIR)/"

install-lib:
	$(MAKE) -C lib install

install-doc:
	mkdir -p "$(DOCDIR)"
	cp -r doc/* "$(DOCDIR)/"

