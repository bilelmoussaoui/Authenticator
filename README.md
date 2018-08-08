[![Translation status](https://hosted.weblate.org/widgets/authenticator/-/svg-badge.svg)](https://hosted.weblate.org/engage/authenticator/?utm_source=widget) [![Version](https://img.shields.io/badge/version-0.2.1-green.svg)](https://github.com/bilelmoussaoui/Authenticator/releases)

# Authenticator
<img src="https://raw.githubusercontent.com/bilelmoussaoui/Authenticator/master/data/icons/hicolor/256x256/apps/com.github.bilelmoussaoui.Authenticator.png" width="128" height="128" />
<p>Two-factor authentication code generator for GNOME. Created with love using Python and Gtk.</p>

## Screenshots

<img src="data/screenshots/screenshot1.png" width="280" /> <img src="data/screenshots/screenshot2.png" width="280" /> <img src="data/screenshots/screenshot3.png" width="280" />

## Features

- QR code scanner
- Beautiful UI
- Huge database of (290+) websites/applications

## Installation

### Flatpak
You can install the flatpak package of the application from flathub using
```
flatpak install flathub com.github.bilelmoussaoui.Authenticator
```


### Building from source code
#### Dependecies

- `Python 3.3+`
- `Gtk 3.16+`
- `meson 0.38+`
- `ninja`
- `pyotp`
- `Pillow`
- `pyzbar` depends on `zbar`
  - `libzbar-dev` on Ubuntu
  - `zbar` on Arch
- `libsecret`

1 - Clone the repository

```bash
git clone https://github.com/bilelmoussaoui/Authenticator && cd ./Authenticator
```

2 - Install Python dependecies

```bash
sudo pip install pyotp pyzbar Pillow meson ninja
```

<sub>PS : In some distributions you will need to use `pip3` instead of `pip` to install the compatible version of the package with Python 3.</sub> <br>

3 - Install System dependencies

```bash
sudo apt install gobject-introspection libgirepository1.0-dev libgtk-3-dev
```

4 - Afterwards

```bash
meson builddir
sudo ninja -C builddir install
```

5 - You can run the application from the desktop file or from terminal using
```bash
authenticator
```

## Flags

- `--debug`
  Open the application with debug flags

- `--version`
  Shows the version number of the application

- `--about`
  Shows the about dialog



## Credits

- Applications/Websites database are from [twofactorauth](https://github.com/2factorauth/twofactorauth), by 2factorauth team
