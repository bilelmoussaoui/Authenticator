<a href="https://hosted.weblate.org/engage/gnome-twofactorauth/?utm_source=widget">
<img src="https://hosted.weblate.org/widgets/gnome-twofactorauth/-/svg-badge.svg" alt="Translation status" />
</a>
![Status](https://img.shields.io/badge/status-stable-green.svg) [![Version](https://img.shields.io/badge/version-0.1.1-green.svg)](https://github.com/bil-elmoussaoui/Gnome-TwoFactorAuth/releases) ![Python
version](https://img.shields.io/badge/python-3.3%2B-blue.svg)
# Gnome TwoFactorAuth
<img src="https://raw.githubusercontent.com/bil-elmoussaoui/Gnome-TwoFactorAuth/master/data/icons/hicolor/48x48/apps/gnome-twofactorauth.png" width="128" height="128" />
<p>Two-factor authentication code generator for Gnome. Created with love using Python and Gtk.</p>
### Dependecies
- `Python 3.3+`
- `Gtk 3.16+`
- `meson` (works only with git version for now)
- `ninja`
- `python-pyotp`
- `python-yaml`
- `python-pillow`
- `zbarlight` depends on `zbar`
    - `libzbar-dev` on Ubuntu
    - `zbar` on Arch
- `GnomeKeyring`
- `gnome-screenshot`

<sub>PS: The application was only tested on Arch with Gtk 3.20+, but it should work nicely with older versions too. Keyboard shortcuts widget won't be shown for older versions.</sub>

### Screenshots

<img src="screenshots/screenshot7.png" width="280" /> <img src="screenshots/screenshot1.png" width="280" /> <img src="screenshots/screenshot2.png" width="280" />

### Features
- QR code scanner
- Beautiful UI
- Handy shortcuts
- Huge database of (290+) websites/applications

### Installation
- On Arch :
```bash
yaourt -S gnome-twofactorauth
```

- On Ubuntu (xenial/yakkety) using GetDeb Apps PPA:
```bash
 wget -q -O - http://archive.getdeb.net/getdeb-archive.key | sudo apt-key add -
sudo sh -c 'echo "deb http://archive.getdeb.net/ubuntu xenial-getdeb apps" >> /etc/apt/sources.list.d/getdeb.list'
sudo apt update
sudo apt install gnome-twofactorauth
 ```

### Credits
- Websites and application icons are from Paper theme, created by [Sam Hewitt](https://github.com/snwh)
- Applications/Websites database are from [twofactorauth](https://github.com/2factorauth/twofactorauth), by 2factorauth team

### How to build from source
1 - Clone the repository
```bash
git clone https://github.com/bil-elmoussaoui/TwoFactorAuth && cd ./TwoFactorAuth
```
2 - Install Python dependecies
```bash
sudo pip install pyotp zbarlight python-yaml pillow
```
<sub>PS : In some distributions you will need to use `pip3` instead of `pip` to install the compatible version of the package with Python 3.</sub> <br>
3 - Afterwards
```bash
mkdir build && cd build
meson ..
ninja 
sudo ninja install
```
4 - You can run the application from the desktop file or from terminal using
```bash
gnome-twofactorauth
```
<sub>Arch users can build from source directly using AUR `yaourt -S gnome-twofactorauth-git`</sub>

### Flags
- `--debug` <br/>
    Open the application with debug flags
- `--version`<br/>
    Shows the version number of the application
- `--about`<br/>
    Shows the about dialog
