[![Translation status](https://hosted.weblate.org/widgets/authenticator/-/svg-badge.svg)](https://hosted.weblate.org/engage/authenticator/?utm_source=widget) [![Version](https://img.shields.io/badge/version-0.2.4-green.svg)](https://github.com/bilelmoussaoui/Authenticator/releases)

# Authenticator
<img src="https://gitlab.gnome.org/World/Authenticator/raw/master/data/icons/hicolor/256x256/apps/com.github.bilelmoussaoui.Authenticator.png" width="128" height="128" />
<p>Two-factor authentication code generator for GNOME. Created with love using Python and GTK+.</p>

## Screenshots

<p align="center">
<img align="center" src="data/screenshots/screenshot1.png" />
</p>

## Features

- QR code scanner
- Beautiful UI
- Huge database of (290+) websites/applications

## Installation

### Flatpak
You can install the `flatpak` package of the application from Flathub using
```
flatpak install flathub com.github.bilelmoussaoui.Authenticator
```


### Building from source code
#### Dependecies

- `Python 3.3+`
- `Gtk 3.16+`
- `meson 0.42+`
- `ninja`
- `pyotp`
- `libsecret`
- `python-gnupg`
- `gnupg`

Those dependencies are only used if you build the application with QR code scanner support
- `Pillow`
- `pyzbar` depends on `zbar`
  - `libzbar-dev` on Ubuntu
  - `zbar` on Arch

1 - Clone the repository

```bash
git clone https://github.com/bilelmoussaoui/Authenticator && cd ./Authenticator
```

2 - Install the dependencies

3 - Afterwards

```bash
meson builddir
sudo ninja -C builddir install
```

4 - You can run the application from the desktop file or from the terminal using
```bash
authenticator
```

## Flags

- `--version`
  Shows the version number of the application
- `--debug`
  Enable the debug logs


## Credits

- Database for applications/websites from [twofactorauth](https://github.com/2factorauth/twofactorauth), by the 2factorauth team
