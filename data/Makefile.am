SUBDIRS = logos

desktopdir = $(datadir)/applications
desktop_DATA = gnome-twofactorauth.desktop

uidir = $(pkgdatadir)/data
ui_DATA = about.ui \
		shortcuts.ui \
		style.css

appdatadir = $(pkgdatadir)/appdata
appdata_DATA = \
	gnome-twofactorauth.appdata.xml

EXTRA_DIST =  \
		$(ui_DATA) \
		$(desktop_DATA) \
		$(appdata_DATA)

CLEANFILES = \
		$(appdata_DATA) \
		$(desktop_DATA)
		$(ui_DATA)

install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)
