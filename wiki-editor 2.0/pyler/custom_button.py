# -*- coding: utf-8 -*-
#pylint: disable=E1101
"""
custom button for languages
"""
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk

from araclar import get_stock, LANGS

class CustomButton(gtk.Button):
    """
    create menu item as a button widget
    """
    def __init__(self, wikieditor, item_list):

        gtk.Button.__init__(self)

        self.gl_b = wikieditor.gl_b
        self.wiki = wikieditor

        menu = gtk.Menu()
        for each in item_list:
            menu_items = gtk.MenuItem(each)
            menu.append(menu_items)
            menu_items.connect("activate", self.menuitem_response, each)
            menu_items.show()

        ekleme = gtk.HBox()
        image = get_stock(gtk.STOCK_GO_DOWN)
        label = gtk.Label("Düz Metin")
        ekleme.pack_start(label, False, False, 10)
        ekleme.pack_start(image, False, False, 0)
        self.gl_b["label"] = label

        self.set_relief(gtk.ReliefStyle.NONE)
        self.connect_object("event", button_press, menu)
        self.add(ekleme)
        self.show()

    def menuitem_response(self, _, string):
        """
        change custom button label text
        """
        self.gl_b["label"].set_text(f"{string}")
        lang = LANGS[ self.gl_b["label"].get_text() ]
        language = self.gl_b["lang_manager"].guess_language(content_type=lang)
        self.wiki.current_buffer.set_language(language)

def button_press(widget, event):
    """
    button press action for STATU the custom button
    """
#    print(widget, event.type)
    if event.type == gdk.EventType.BUTTON_PRESS:
#        if event.button == 1:
        widget.popup(None, None, None, event.button, event.time, event.time)
