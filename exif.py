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

# https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

import gi

gi.require_version("Caja", "2.0")

from gi.repository import Caja, GObject, Gtk


class ExifExtension(GObject.GObject, Caja.PropertyPageProvider):
    def __init__(self):
        pass

    def get_gps_tags(self, exif):
        gps_info = exif.pop("GPSInfo")
        for (k, v) in gps_info.items():
            exif[GPSTAGS.get(k, f"{k} (GPS Tag ID Unknown)")] = v

        return exif

    def get_human_readable_exif(self, filename):
        exif = {}

        try:
            with Image.open(filename) as img:
                img.verify()

                for (k, v) in img.getexif().items():
                    if isinstance(v, (bytes, str)) and len(v) > 64:
                        v = v[:65] + ("..." if isinstance(v, str) else b"...")

                    exif[TAGS.get(k, f"{k} (Tag ID Unknown)")] = v
        except Exception:
            pass

        if "GPSInfo" in exif and isinstance(exif["GPSInfo"], dict):
            exif = self.get_gps_tags(exif)

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

        store = Gtk.ListStore.new([str, str])
        for (k, v) in exif.items():
            store.append([str(k), str(v)])

        column = Gtk.TreeViewColumn.new()

        tag_name = Gtk.CellRendererText.new()
        column.pack_start(tag_name, True)
        column.add_attribute(tag_name, "text", 0)

        value = Gtk.CellRendererText.new()
        column.pack_start(value, True)
        column.add_attribute(value, "text", 1)

        tree_view = Gtk.TreeView.new_with_model(store)
        tree_view.set_headers_visible(False)
        tree_view.append_column(column)
        tree_view.show()

        scroller = Gtk.ScrolledWindow.new(None, None)
        scroller.add(tree_view)
        scroller.show()

        return (Caja.PropertyPage(name="CajaPython::exif",
                                  label=label,
                                  page=scroller),)

# vim: ts=4 et
