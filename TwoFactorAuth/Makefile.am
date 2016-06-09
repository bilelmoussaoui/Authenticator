app_PYTHON = \
	application.py \
	__init__.py 
do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
	-e 's,[@]localedir[@],$(localedir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' \
	-e 's,[@]pyexecdir[@],$(pyexecdir),g'



appdir = $(pythondir)/Gnome-TwoFactorAuth

SUBDIRS = models \
          widgets
