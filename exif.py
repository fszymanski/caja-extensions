# Copyright (C) 2021 Filip Szymański <fszymanski.pl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

from PIL import Image
from PIL.ExifTags import TAGS

import gi

gi.require_version("Caja", "2.0")

from gi.repository import Caja, GObject, Gtk


class ExifExtension(GObject.GObject, Caja.PropertyPageProvider):
    def __init__(self):
        pass

    def get_human_readable_exif(self, filename):
        exif = {}

        try:
            with Image.open(filename) as img:
                img.verify()

                for (k, v) in img.getexif().items():
                    if isinstance(v, (bytes, str)) and len(v) > 128:
                        v = v[:129] + ("..." if isinstance(v, str) else b'...')

                    exif[TAGS.get(k, f"{k} (Unknown)")] = v
        except Exception:
            pass

        return exif

    def get_property_pages(self, files):
        if len(files) != 1:
            return

        file = files[0]
        if (file.get_uri_scheme() != "file") or file.is_directory():
            return

        filename = file.get_location().get_path()
        exif = self.get_human_readable_exif(filename)
        if not exif:
            return

        label = Gtk.Label.new("Exif")
        label.show()

        text_view = Gtk.TextView.new()
        text_view.set_cursor_visible(False)
        text_view.set_editable(False)
        text_view.set_wrap_mode(Gtk.WrapMode.CHAR)
        text_view.show()

        buf = text_view.get_buffer()
        buf.set_text("\n".join([f"{k}: {v}" for k, v in exif.items()]))

        scroller = Gtk.ScrolledWindow.new(None, None)
        scroller.add(text_view)
        scroller.show()

        return (Caja.PropertyPage(name="CajaPython::exif",
                                  label=label,
                                  page=scroller),)

# vim: ts=4 et
