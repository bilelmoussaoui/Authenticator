desktopdir = $(DATADIR)/applications
desktop_DATA = two-factor.desktop

UPDATE_DESKTOP = update-desktop-database $(datadir)/applications || :

uidir = $(pkgdatadir)/data
ui_DATA = about.glade
appdatadir = $(DATADIR)/appdata
appdata_DATA = \
    two-factor.appdata.xml

EXTRA_DIST =  \
        $(ui_DATA) \
        $(appdata_DATA)

CLEANFILES = \
    	$(appdata_DATA)

install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)
