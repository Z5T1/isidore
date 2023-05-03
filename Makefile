DESTDIR=/opt/isidore
BINDIR=$(DESTDIR)/bin
DOCDIR=$(DESTDIR)/doc

.PHONY: install install-bin install-doc

install: install-bin install-doc

install-bin:
	mkdir -p "$(BINDIR)"
	cp -r bin/* "$(BINDIR)/"

install-doc:
	mkdir -p "$(DOCDIR)"
	cp -r doc/* "$(DOCDIR)/"

