appdir = $(pythondir)/TwoFactorAuth/models
do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' \
	-e 's,[@]pyexecdir[@],$(pyexecdir),g'

app_PYTHON = \
	code.py \
	authenticator.py \
	settings.py
