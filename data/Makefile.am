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

# hicolor icons
hicolor_icon16dir = $(datadir)/icons/hicolor/16x16/apps
hicolor_icon16_DATA = icons/hicolor/16x16/apps/gnome-twofactorauth.png
hicolor_icon22dir = $(datadir)/icons/hicolor/22x22/apps
hicolor_icon22_DATA = icons/hicolor/22x22/apps/gnome-twofactorauth.png
hicolor_icon32dir = $(datadir)/icons/hicolor/32x32/apps
hicolor_icon32_DATA = icons/hicolor/32x32/apps/gnome-twofactorauth.png
hicolor_icon48dir = $(datadir)/icons/hicolor/48x48/apps
hicolor_icon48_DATA = icons/hicolor/48x48/apps/gnome-twofactorauth.png
hicolor_icon256dir = $(datadir)/icons/hicolor/256x256/apps
hicolor_icon256_DATA = icons/hicolor/256x256/apps/gnome-twofactorauth.png
hicolor_iconscalabledir = $(datadir)/icons/hicolor/scalable/apps
hicolor_iconscalable_DATA = icons/hicolor/scalable/apps/gnome-twofactorauth-symbolic.svg
hicolor_icon_files = \
	$(hicolor_icon16_DATA) \
	$(hicolor_icon22_DATA) \
	$(hicolor_icon32_DATA) \
	$(hicolor_icon48_DATA) \
	$(hicolor_icon256_DATA) \
	$(hicolor_iconscalable_DATA)

gtk_update_hicolor_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor
gtk_update_hicontrast_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/HighContrast

update-icon-cache:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk hicolor icon cache."; \
		$(gtk_update_hicolor_icon_cache); \
		echo "Updating Gtk highcontrast icon cache."; \
		$(gtk_update_hicontrast_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After (un)install, run this:"; \
		echo "***   $(gtk_update_hicolor_icon_cache)"; \
		echo "***   $(gtk_update_hicolor_icon_cache)"; \
	fi

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
	$(UPDATE_DESKTOP) \
	$(update-icon-cache)
uninstall-hook:
	$(UPDATE_DESKTOP) \
	$(update-icon-cache)

all-local: gschemas.compiled
