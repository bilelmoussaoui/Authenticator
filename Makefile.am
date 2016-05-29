bin_SCRIPTS = twofactorauth
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = twofactorauth.in

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
	-e 's,[@]localedir[@],$(localedir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' \
	-e 's,[@]pyexecdir[@],$(pyexecdir),g'

twofactorauth: twofactorauth.in Makefile
	$(do_substitution) < $(srcdir)/twofactorauth.in > twofactorauth
	chmod +x twofactorauth

SUBDIRS = TwoFactorAuth \
          data \
          po
