SUBDIRS = unitsconverter

bin_SCRIPTS = units-converter
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = unit-converter.in

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' 

units-converter: units-converter.in Makefile
	$(do_substitution) < $(srcdir)/units-converter.in > units-converter
	chmod +x units-converter
