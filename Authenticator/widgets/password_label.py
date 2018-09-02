from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk


class PasswordLabel(Gtk.EventBox):
    visibility = True
    _text = None

    def __init__(self, text=None):
        Gtk.EventBox.__init__(self)
        self.connect("button-press-event", self._event_handler)
        self._lbl = Gtk.Label()
        self.text = text
        self._build_widgets()
        self.show()

    def _build_widgets(self):
        self.add(self._lbl)

    def _event_handler(self, *args):
        self.set_visibility(not self.get_visibility())

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if text is None:
            text = ""
        self._text = text
        self._lbl.set_text(text)

    def set_visibility(self, state):
        self.visibility = state
        if not self.visibility:
            self._lbl.set_text("●"*len(self.text))
        else:
            self._lbl.set_text(self.text)

    def get_visibility(self):
        return self.visibility
