AC_INIT([TwoFactorAuth], [0.1], [https://github.com/bil-elmoussaoui/TwoFactorAuth])

AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_HEADERS(config.h)

AM_INIT_AUTOMAKE
AM_PATH_PYTHON([3.0])
AM_MAINTAINER_MODE([enable])
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])


GETTEXT_PACKAGE=TwoFactorAuth
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE",
                   [The prefix for our gettext translation domains.])
IT_PROG_INTLTOOL(0.26)

GLIB_GSETTINGS
GOBJECT_INTROSPECTION_REQUIRE([1.35.9])
PKG_CHECK_MODULES([GTK], [gtk+-3.0 >= 3.16.0])


GLIB_COMPILE_RESOURCES=`$PKG_CONFIG --variable glib_compile_resources gio-2.0`
AC_SUBST(GLIB_COMPILE_RESOURCES)

AC_CONFIG_FILES([
    Makefile
    data/Makefile
    data/logos/Makefile
    data/twofactorauth.desktop
    TwoFactorAuth/Makefile
    TwoFactorAuth/models/Makefile
    TwoFactorAuth/widgets/Makefile
    schemas/Makefile
	po/Makefile.in
])

AC_OUTPUT
