
message('TODO: Making a list of icons')
subdir('icons')

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
  install_dir : join_paths(get_option('prefix'),get_option('datadir'), 'glib-2.0/schemas')
)

i18n.merge_file(
  output: meson.project_name() + '.desktop',
  input: meson.project_name() + '.desktop.in',
  po_dir: join_paths(meson.source_root(), 'po'),
  type: 'desktop',
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)

i18n.merge_file(
  output: meson.project_name() + '.appdata.xml',
  input: meson.project_name() + '.appdata.xml.in',
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'appdata')
)



desktop_file_validate = find_program('desktop-file-validate', required:false)

if desktop_file_validate.found()
  test (
    'Validate desktop file',
    desktop_file_validate,
    args: join_paths(meson.current_build_dir (), meson.project_name() + '.desktop')
  )
endif

appstreamcli = find_program('appstream-util', required:false)

if appstreamcli.found()
  test (
    'Validate appdata file',
    appstreamcli,
    args: ['validate-relax', join_paths(meson.current_build_dir (), meson.project_name() + '.appdata.xml')]
  )
endif
