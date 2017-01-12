gnome = import('gnome')


subdir('applications')
build_dir = get_option('prefix') + '/' + get_option('datadir')
po_dir = get_option('prefix') + '/' + get_option('datadir') + '/locale'
message('TODO: Compiling resources')
gnome.compile_resources(
     'org.gnome.Authenticator', 'org.gnome.Authenticator.gresource.xml',
     gresource_bundle: true,
     source_dir : '.',
     install_dir : build_dir + '/Authenticator',
     install: true)


message('Compiling schemas')
gnome.compile_schemas()
install_data(
    'org.gnome.Authenticator.gschema.xml',
    install_dir : 'share/glib-2.0/schemas')

message('TODO: Making a .desktop file')
custom_target('org.gnome.Authenticator.desktop',
	output : 'org.gnome.Authenticator.desktop',
	input : 'org.gnome.Authenticator.desktop.in',
	command : [intltool_merge, '--desktop-style', po_dir, '@INPUT@', '@OUTPUT@'],
	install : true,
	install_dir : get_option('datadir') + '/applications'
	)

message('TODO: Preparing appdata')
custom_target('org.gnome.Authenticator.appdata.xml',
    output : 'org.gnome.Authenticator.appdata.xml',
    input : 'org.gnome.Authenticator.appdata.xml.in',
    command : [intltool_merge, '--xml-style', po_dir, '@INPUT@', '@OUTPUT@'],
    install : true,
    install_dir : get_option('datadir') + '/appdata'
    )

message('TODO: Making a list of icons')
subdir('icons')

