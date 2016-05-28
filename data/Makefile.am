SUBDIRS = logos

desktopdir = $(datadir)/applications
desktop_DATA = twofactorauth.desktop

uidir = $(pkgdatadir)/data
ui_DATA = about.glade \
        shortcuts.glade \
        menu.glade \
        style.css

appdatadir = $(pkgdatadir)/appdata
appdata_DATA = \
    twofactorauth.appdata.xml

EXTRA_DIST =  \
        $(ui_DATA) \
        $(desktop_DATA) \
        $(appdata_DATA)

CLEANFILES = \
    	$(appdata_DATA)

install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)
