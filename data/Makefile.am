resource_files = $(shell $(GLIB_COMPILE_RESOURCES) --sourcedir=$(srcdir) --sourcedir=$(builddir) --generate-dependencies $(builddir)/gnome-twofactorauth.gresource.xml)
gnome-twofactorauth.gresource: gnome-twofactorauth.gresource.xml $(resource_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --target=$@ --sourcedir=$(srcdir) --sourcedir=$(builddir) $<

resourcedir = $(pkgdatadir)
resource_DATA = gnome-twofactorauth.gresource

SUBDIRS = applications

desktopdir = $(datadir)/applications
desktop_DATA = gnome-twofactorauth.desktop

appdatadir = $(pkgdatadir)/appdata
appdata_DATA = \
	gnome-twofactorauth.appdata.xml

EXTRA_DIST =  \
		$(resource_files) \
		$(desktop_DATA) \
		$(appdata_DATA)

CLEANFILES = \
		$(appdata_DATA) \
		$(desktop_DATA) \
		$(resource_files) \

install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)
