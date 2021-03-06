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

import gi

gi.require_version('Caja', '2.0')
gi.require_version('GExiv2', '0.10')
gi.require_version('Gtk', '3.0')
from gi.repository import Caja, GExiv2, GLib, GObject, Gtk


class ExifExtension(GObject.GObject, Caja.PropertyPageProvider):
    def __init__(self):
        pass

    def get_exif(self, filename):
        exif = {}

        metadata = GExiv2.Metadata.new()
        try:
            metadata.open_path(filename)
        except GLib.Error:
            pass
        else:
            if metadata.has_exif():
                for tag in metadata.get_exif_tags():
                    try:
                        value = metadata.try_get_tag_interpreted_string(tag)
                        exif[tag.split(".")[-1]] = (f'{value[:65]}...' if len(value) > 64 else value)
                    except GLib.Error:
                        pass

        return exif

    def get_property_pages(self, files):
        if len(files) != 1:
            return None

        file = files[0]
        if (file.get_uri_scheme() != 'file') or file.is_directory():
            return None

        filename = file.get_location().get_path()
        exif = self.get_exif(filename)
        if not exif:
            return None

        label = Gtk.Label.new('Exif')
        label.show()

        store = Gtk.ListStore.new([str, str])
        for t, v in sorted(exif.items()):
            store.append([t, v])

        tree_view = Gtk.TreeView.new_with_model(store)
        tree_view.show()

        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn('Tag', renderer, text=0)
        tree_view.append_column(column)

        renderer = Gtk.CellRendererText.new()
        column = Gtk.TreeViewColumn('Value', renderer, text=1)
        tree_view.append_column(column)

        scroller = Gtk.ScrolledWindow.new(None, None)
        scroller.add(tree_view)
        scroller.show()

        return (Caja.PropertyPage(name='CajaPython::exif',
                                  label=label,
                                  page=scroller),)

# vim: ft=python3 ts=4 et
