gnome = import('gnome')


subdir('applications')
build_dir = get_option('prefix') + '/' + get_option('datadir')
po_dir = get_option('prefix') + '/' + get_option('datadir') + '/locale'
message('TODO: Compiling resources')
gnome.compile_resources(
     'gnome-twofactorauth', 'gnome-twofactorauth.gresource.xml',
     gresource_bundle: true,
     source_dir : '.',
     install_dir : build_dir + '/TwoFactorAuth',
     install: true)


message('Compiling schemas')
gnome.compile_schemas()
install_data(
    'org.gnome.TwoFactorAuth.gschema.xml',
    install_dir : 'share/glib-2.0/schemas')

message('TODO: Making a .desktop file')
custom_target('gnome-twofactorauth.desktop',
	output : 'gnome-twofactorauth.desktop',
	input : 'gnome-twofactorauth.desktop.in',
	command : [intltool_merge, '--desktop-style', po_dir, '@INPUT@', '@OUTPUT@'],
	install : true,
	install_dir : get_option('datadir') + '/applications'
	)

message('TODO: Preparing appdata')
custom_target('gnome-twofactorauth.appdata.xml',
    output : 'gnome-twofactorauth.appdata.xml',
    input : 'gnome-twofactorauth.appdata.xml.in',
    command : [intltool_merge, '--xml-style', po_dir, '@INPUT@', '@OUTPUT@'],
    install : true,
    install_dir : get_option('datadir') + '/appdata'
    )

message('TODO: Making a list of icons')
subdir('icons')

