![Status](https://img.shields.io/badge/status-stable-green.svg) [![Version](https://img.shields.io/badge/version-0.1beta2-green.svg)](https://github.com/bil-elmoussaoui/Gnome-TwoFactorAuth/releases) ![Python
version](https://img.shields.io/badge/python-3.3%2B-blue.svg)

# Gnome TwoFactorAuth
Two-factor authentication code generator for Gnome <br>
For translators : https://www.transifex.com/twofactorauth/twofactorauth/
### Dependecies
- `Python 3.3+`
- `Gtk 3.16+`
- `PyOTP`
- `zbarlight`
- `yaml`
- `GnomeKeyring`

<sub>PS: The application was only tested on Arch with Gtk 3.20+, but it should work nicely with older versions too. Keyboard shortcuts widget won't be shown for older versions.</sub>

### Screenshots

<img src="screenshots/screenshot7.png" width="280" /> <img src="screenshots/screenshot1.png" width="280" /> <img src="screenshots/screenshot2.png" width="280" />


### Installation
- On Arch :
```bash
    yaourt -S gnome-twofactourauth
```

### Credits
- Websites and application icons are from Paper theme, created by [Sam Hewitt](https://github.com/snwh)
- Applications/Websites database are from [twofactorauth](https://github.com/2factorauth/twofactorauth), by 2factorauth team

### How to build from source
1 - Clone the repository
```bash
    git clone https://github.com/bil-elmoussaoui/TwoFactorAuth && cd ./TwoFactorAuth
```
2 - Install `PyOTP`
```bash
    sudo pip install pyotp
```
3 - Install `zbarlight`
```bash
sudo pip install zbarlight
```
4 - Install `yaml`
```bash
sudo pip install pyyaml
```

<sub>PS : In some distributions you will need to use `pip3` instead of `pip` to install the compatible version of the package with Python 3.</sub> <br>
5 - Afterwards
```bash
    ./autogen.sh
    make
    sudo make install
```
6 - You can run the application from the desktop file or from terminal using
```bash
    gnome-twofactorauth
```
<sub>Arch users can build from source directly using AUR `yaourt -S gnome-twofactorauth-git`</sub>
