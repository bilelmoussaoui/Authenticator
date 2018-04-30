icon_themes = ['hicolor']
sizes = ['16x16', '22x22', '24x24', '32x32', '48x48', '256x256', 'scalable']
foreach theme : icon_themes
  foreach size: sizes
    extension = '.png'
    if size == 'scalable'
      extension = '.svg'
    endif
    icon_dir = join_paths(theme, size , 'apps')
    icon_name = join_paths(icon_dir, meson.project_name() + extension)
    dest = join_paths(get_option('prefix'), 'share/icons', icon_dir)
    install_data(icon_name, install_dir: dest)
  endforeach
  symbolic_dir = join_paths(theme, 'symbolic/apps/')
  symbolic_icon = join_paths(symbolic_dir, meson.project_name() + '-symbolic.svg')
  dest_symbolic = join_paths(get_option('prefix'), 'share/icons', symbolic_dir)
  install_data(symbolic_icon,
              install_dir: dest_symbolic)
endforeach

