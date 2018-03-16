<a href="https://hosted.weblate.org/engage/Authenticator/?utm_source=widget"><img src="https://hosted.weblate.org/widgets/Authenticator/-/svg-badge.svg" alt="Translation status" /></a> ![Status](https://img.shields.io/badge/status-stable-green.svg) [![Version](https://img.shields.io/badge/version-0.1.1-green.svg)](https://github.com/bilelmoussaoui/Authenticator/releases) ![Python
version](https://img.shields.io/badge/python-3.3%2B-blue.svg)

# Authenticator
<img src="https://raw.githubusercontent.com/bilelmoussaoui/Authenticator/master/data/icons/hicolor/256x256/apps/com.github.bilelmoussaoui.Authenticator.png" width="128" height="128" />
<p>Two-factor authentication code generator for Gnome. Created with love using Python and Gtk.</p>

### Dependecies

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
- `gnome-screenshot`

<sub>
PS: The application was only tested on Arch with Gtk 3.20+, but it should work nicely with older versions too. Keyboard shortcuts widget won't be shown for older versions.
</sub>

### Screenshots

<img src="data/screenshots/screenshot1.png" width="280" /> <img src="data/screenshots/screenshot4.png" width="280" /><br>
<img src="data/screenshots/screenshot2.png" width="280" /><img src="data/screenshots/screenshot3.png" width="280" />

### Features

- QR code scanner
- Beautiful UI
- Huge database of (290+) websites/applications

### Credits

- Websites and application icons are from Paper theme, created by [Sam Hewitt](https://github.com/snwh)
- Applications/Websites database are from [Authenticator](https://github.com/2factorauth/Authenticator), by 2factorauth team

### How to build from source

1 - Clone the repository

```bash
git clone https://github.com/bilelmoussaoui/Authenticator && cd ./Authenticator
```

2 - Install Python dependecies

```bash
sudo pip install pyotp zbarlight pyaml Pillow meson ninja
```

<sub>PS : In some distributions you will need to use `pip3` instead of `pip` to install the compatible version of the package with Python 3.</sub> <br>

3 - Afterwards

```bash
meson builddir
sudo ninja -C builddir install
```

4 - You can run the application from the desktop file or from terminal using
```bash
authenticator
```

### Flags

- `--debug`
  Open the application with debug flags

- `--version`
  Shows the version number of the application

- `--about`
  Shows the about dialog
