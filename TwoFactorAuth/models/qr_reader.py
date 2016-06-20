from PIL import Image
import zbarlight
from urllib.parse import urlparse, parse_qsl
import logging
from os import remove, path
from TwoFactorAuth.models.code import Code

class QRReader:

    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename, 'rb') as image_file:
            image = Image.open(image_file)
            image.load()
        self.codes = zbarlight.scan_codes('qrcode', image)
        if self.codes:
            otpauth_url = self.codes[0].decode()
            self.codes = dict(parse_qsl(urlparse(otpauth_url)[4]))
            return self.codes
        else:
            logging.error("Invalid QR image")
            return None

    def remove(self):
        """
            remove image file for security reasons
        """
        if path.isfile(self.filename):
            remove(filename)
            logging.debug("QR code image was removed for security reasons")

    def is_valid(self):
        if isinstance(self.codes, dict):
            if set(["issuer", "secret"]).issubset(self.codes.keys()):
                return Code.is_valid(self.codes["secret"])
            else:
                return False
        else:
            return False
