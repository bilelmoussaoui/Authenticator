message('TODO: Compiling resources')
gnome.compile_resources(
  meson.project_name(),
  meson.project_name() + '.gresource.xml',
  gresource_bundle: true,
  source_dir: '.',
  install_dir: DATA_DIR,
  install: true
)

message('Compiling schemas')
install_data(
  meson.project_name() + '.gschema.xml',
  install_dir : join_paths(get_option('prefix'), 'share/glib-2.0/schemas')
)

i18n.merge_file(
  output: meson.project_name() + '.desktop',
  input: meson.project_name() + '.desktop.in',
  po_dir: '../po',
  type: 'desktop',
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)

i18n.merge_file(
  output: meson.project_name() + '.appdata.xml',
  input: meson.project_name() + '.appdata.xml.in',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'appdata')
)

message('TODO: Making a list of icons')
subdir('icons')

