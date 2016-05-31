![Status](https://img.shields.io/badge/version-alpha-red.svg) ![Python version](https://img.shields.io/badge/python-3.4%2C%203.5-blue.svg)

# TwoFactorAuth
Two-factor authentication generator for Gnome <br>
For translators : https://www.transifex.com/twofactorauth/twofactorauth/
### Dependecies 
- `Python 3.3+`
- `Gtk 3.16+`
- `PyOTP`
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

### How to build from source
1 - Clone the repository
```bash
    git clone https://github.com/bil-elmoussaoui/TwoFactorAuth && cd ./TwoFactorAuth
```
2 - Install `PyOTP`
```bash
    sudo pip install pyotp
```
<sub>PS : In some distributions you will need to use `pip3` instead of `pip` to install the compatible version of the package with Python 3.</sub> <br>
3 - Afterwards
```bash
    ./autogen.sh
    make
    sudo make install
```
4 - You can run the application from the desktop file or from terminal using 
```bash
    twofactorauth
```
<sub>Arch users can build from source directly using AUR <br/></sub> 
```bash
    yaourt -S gnome-twofactorauth
```
