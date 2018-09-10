configure_file(
  input: 'authenticator-search-provider.py.in',
  output: 'authenticator-search-provider',
  configuration: conf,
  install_dir: LIBEXEC_DIR
)
configure_file(
  input: meson.project_name() + '.SearchProvider.service.in',
  output: meson.project_name() + '.SearchProvider.service',
  configuration: conf,
  install_dir: SERVICES_DIR
)
install_data(
  'authenticator-search-provider.ini',
  install_dir: SEARCH_PROVIDER_DIR
)
