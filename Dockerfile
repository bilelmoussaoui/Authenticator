FROM ubuntu:16.04
RUN apt-get -y update
# Install dependecies
RUN apt-get install -y python3 libzbar-dev gnome-screenshot gnome-keyring git python-gobject
RUN pip install python-pyotp python-yaml python-pillow zbarlight setuptools
RUN pip install ninja 
# Install latest git version of meson
RUN git clone https://github.com/mesonbuild/meson && && cd ./meson && python3 setup.py install 
# Build Gnome-TwoFactorAuth usinn Meson
RUN git clone https://github.com/bil-elmoussaoui/Gnome-TwoFactorAuth && cd ./Gnome-TwoFactorAuth 
RUN mkdir build && cd ./build
RUN meson .. && ninja && sudo ninja install

CMD gnome-twofactorauth