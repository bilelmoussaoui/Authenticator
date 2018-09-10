project('com.github.bilelmoussaoui.Authenticator',
	version: '0.2.4',
  meson_version: '>= 0.42',
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


use_zbar = false
if get_option('enable-zbar')
  use_zebar = true
endif

python_bin = python.find_python()
if not python_bin.found()
    error('No valid python3 binary found')
else
    message('Found python3 binary')
endif

PYTHON_DIR = join_paths(get_option('prefix'), python.sysconfig_path('purelib'))
DATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
LOCALE_DIR = join_paths(get_option('prefix'), get_option('localedir'))
LIB_DIR = join_paths(get_option('prefix'), get_option('libdir'), meson.project_name())
SERVICES_DIR = join_paths(get_option('datadir'), 'dbus-1', 'services')
SEARCH_PROVIDER_DIR = join_paths(get_option('datadir'), 'gnome-shell', 'search-providers')
LIBEXEC_DIR = join_paths(get_option('prefix'), get_option('libexecdir'))

subproject('libgd',
  default_options: [
    'with-introspection=true',
    'with-notification=true',
    'static=false',
    'pkgdatadir=' + DATA_DIR,
    'pkglibdir=' + LIB_DIR
  ]
)



# Configuration params
conf = configuration_data()
conf.set('DATA_DIR', DATA_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PYTHON_DIR', PYTHON_DIR)
conf.set('PYTHON_EXEC_DIR', join_paths(get_option('prefix'), python.sysconfig_path('stdlib')))
conf.set('VERSION', meson.project_version())
conf.set('ENABLE_QRSCANNER', use_zbar)
conf.set('LIB_DIR', LIB_DIR)
conf.set('libexecdir', LIBEXEC_DIR)
conf.set('PYTHON', python_bin.path())

subdir('data')
subdir('po')
subdir('search-provider')

configure_file(
  input: 'authenticator.py.in',
  output: 'authenticator',
  configuration: conf,
  install_dir: join_paths(get_option('prefix'), get_option('bindir'))
)

configure_file(
  input: 'Authenticator/widgets/about.py.in',
  output: 'about.py',
  configuration: conf,
  install_dir : join_paths(PYTHON_DIR, 'Authenticator/widgets')
)


install_subdir(
  'Authenticator',
  install_dir: PYTHON_DIR,
  exclude_files: 'widgets/about.py.in'
)

meson.add_install_script('tools/build/meson_post_install.py')
