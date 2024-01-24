DESTDIR=
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin
DOCDIR=$(PREFIX)/share/doc/isidore

.PHONY: install install-bin install-doc all clean

all:
	$(MAKE) -C lib

clean:
	$(MAKE) -C lib clean

install: install-bin install-doc install-lib

install-bin:
	mkdir -p "$(DESTDIR)$(BINDIR)"
	cp -r bin/* "$(DESTDIR)$(BINDIR)/"

install-lib:
	$(MAKE) -C lib install

install-doc:
	mkdir -p "$(DESTDIR)$(DOCDIR)"
	cp -r doc/* "$(DESTDIR)$(DOCDIR)/"

