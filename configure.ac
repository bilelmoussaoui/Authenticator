AC_INIT([TwoFactorAuth], [0.1], [https://github.com/bil-elmoussaoui/TwoFactorAuth])

AM_INIT_AUTOMAKE
AM_PATH_PYTHON([3.0])

GOBJECT_INTROSPECTION_REQUIRE([1.35.9])
PKG_CHECK_MODULES([GTK], [gtk+-3.0 >= 3.18.0])

AC_CONFIG_FILES([
    Makefile
    data/Makefile
    data/logos/Makefile
    data/twofactorauth.desktop
    TwoFactorAuth/Makefile
    TwoFactorAuth/models/Makefile
    TwoFactorAuth/ui/Makefile
])

AC_OUTPUT
