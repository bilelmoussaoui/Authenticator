SUBDIRS = applications

resource_files = $(shell $(GLIB_COMPILE_RESOURCES) --sourcedir=$(srcdir) --sourcedir=$(builddir) --generate-dependencies $(builddir)/gnome-twofactorauth.gresource.xml)
gnome-twofactorauth.gresource: gnome-twofactorauth.gresource.xml $(resource_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --target=$@ --sourcedir=$(srcdir) --sourcedir=$(builddir) $<



resourcedir = $(pkgdatadir)
resource_DATA = gnome-twofactorauth.gresource

desktopdir = $(datadir)/applications
desktop_DATA = gnome-twofactorauth.desktop

@INTLTOOL_DESKTOP_RULE@

appdatadir = $(pkgdatadir)/appdata
appdata_DATA = $(appdata_in_files:.xml.in=.xml)
appdata_in_files = gnome-twofactorauth.appdata.xml.in

@INTLTOOL_XML_RULE@

gsettings_SCHEMAS = org.gnome.TwoFactorAuth.gschema.xml

gschemas.compiled: $(gsettings_SCHEMAS) Makefile
	$(AM_V_GEN) $(GLIB_COMPILE_SCHEMAS) $(builddir)

@GSETTINGS_RULES@

EXTRA_DIST =  \
		$(resource_files) \
		$(desktop_DATA) \
		$(appdata_DATA) \
		gnome-twofactorauth.gresource.xml \
		org.gnome.TwoFactorAuth.gschema.xml

CLEANFILES = \
		gnome-twofactorauth.gresource \
		gnome-twofactorauth.appdata.xml \
		$(desktop_DATA) \
		*.valid \
		gschemas.compiled

install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)

all-local: gschemas.compiled
