project('com.github.bilelmoussaoui.Authenticator',
	version: '0.1.2',
  meson_version: '>= 0.40',
  license: 'GPL+-3.0',
  default_options: ['prefix=/usr']
)
python = import('python3')
gnome  = import('gnome')
i18n   = import('i18n')

message('Looking for dependencies')
dependency('glib-2.0')
dependency('gobject-2.0')
dependency('gobject-introspection-1.0')
dependency('gtk+-3.0', version : '>=3.16')



PYTHON_DIR = join_paths(get_option('prefix'), python.sysconfig_path('purelib'))
DATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
LOCALE_DIR = join_paths(get_option('prefix'), get_option('localedir'))


# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', DATA_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PYTHON_DIR', PYTHON_DIR)
conf.set('VERSION', meson.project_version())

subdir('data')
subdir('po')

install_subdir(
  'Authenticator',
  install_dir: PYTHON_DIR
)

configure_file(
  input: 'authenticator.py.in',
  output: 'authenticator',
  configuration: conf,
  install_dir: join_paths(get_option('prefix'), get_option('bindir'))
)


meson.add_install_script('tools/build/meson_post_install.py')
