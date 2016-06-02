ACLOCAL_AMFLAGS = -I m4
NULL =

bin_SCRIPTS = gnome_twofactorauth
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = gnome-twofactorauth.in

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
	-e 's,[@]localedir[@],$(localedir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' \
	-e 's,[@]pyexecdir[@],$(pyexecdir),g'

gnome_twofactorauth: gnome-twofactorauth.in Makefile
	$(do_substitution) < $(srcdir)/gnome-twofactorauth.in > gnome-twofactorauth
	chmod +x gnome-twofactorauth

SUBDIRS = TwoFactorAuth \
          data \
          po \
		  schemas
