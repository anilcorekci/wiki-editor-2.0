# -*- coding: utf-8 -*-
#pylint: disable=E1101
"""
TOOL BUTTON BUILD FOR ARACLAR
"""

from gi.repository import Gtk as gtk
from kategori import CategoryWindow
from araclar import mesaj

class ToolItem():
    """
    create tooltiem via getting args:
        label, tooltip, resim, islem
    """

    def __init__(self, *args):

        wikieditor, label, tooltip, resim, islem = args

        self.set_text = wikieditor.set_text
        self.gl_b = wikieditor.gl_b
        self.get_konu = wikieditor.get_konu
        self.current_editor = wikieditor.current_editor
        self.ileti = wikieditor.ileti

        item = gtk.ToolButton(resim, label)
        item.set_tooltip_text(tooltip)
        item.set_label(label)
        item.set_icon_widget(resim)

        type_of_islem = type(islem)

        if type_of_islem is dict:
        # if islem is dict unpack dict and call sablon
            file_path, format_ = list( i for i in islem.items() )[0]
            item.connect('clicked', lambda _: self.sablon(file_path, format_))

        elif type_of_islem is list:
        # if islem is list modify selection_ of text
            item.connect('clicked',
                lambda _: self.set_text(f"{islem[0]}{self.get_konu()}{islem[1]}" )
                if self.get_konu()
                else self.ileti.set_text("Seçili hiç bir metin yok !")
            )

        # !!! if it's a string call it as a fuction within ToolItem class...
        elif type_of_islem is str:
            item.connect('clicked', getattr(self, islem))
        # if it's a fuction leave it as it is...
        else:
            item.connect('clicked',islem )

        item.show()
        self.gl_b["tool_active"].insert(item, -1)

    def sablon(self, dosya, format_):
        """
        Build glade files from given path
        """
        builder = gtk.Builder()
        builder.add_from_file( dosya )
        vbox = builder.get_object("vbox1")
        pencere = builder.get_object("window1")
        pencere.set_modal(True)

        dict_= {}
        range_ = len(format_.split("{}"))  # number of entries
        en_, lb_ = [ [1, range_], [range_, range_*2]]

        for _en, _lb in zip(range(*en_), range(*lb_) ):
            dict_[_en] = builder.get_object(f"entry{_en}")
            dict_[_lb] = builder.get_object(f"label{_en}")

        ekle = gtk.Button(" Tamam ")
        ekle.connect("clicked", lambda _:
            self.set_en_label_text(dict_,en_, lb_,format_, pencere) )

        vbox.add(ekle)
        pencere.show_all()

    def set_en_label_text(self, *args):
        """
        order and apply actions for custom glade files
        """

        dict_, en_, lb_, format_, pencere = args

        get_text = []
        for _en, _lb in zip(range(*en_), range(*lb_) ):

            if not dict_[_en].get_text():
                mesaj(f"{ dict_[_lb].get_text() }\nBoş bırakılmamalı!")
                return False

            get_text.append(dict_[_en].get_text())

        self.set_text(format_.format(*get_text), True)
        pencere.destroy()
        return True

    def color_select(self, *_):
        """
        build and show color selection apply to text with <span color>
        """
        if konu:= self.get_konu():
            renksec = gtk.ColorSelectionDialog("Bir renk seçin")
            renksec.set_icon_from_file("../Simgeler/07-renk seç.png")
            renksec.show()

            if renksec.run() == gtk.ResponseType.OK:
                rbg = [ i * 255 for i in
                        renksec.get_color_selection().\
                        get_current_color().\
                        to_floats() ]
                # crazy stuff here needs to change rgb01 to rgb250
                self.set_text(f'<span style="color:rgb({rbg[0]},'+
                              f'{rbg[1]}, {rbg[2]} );">{konu}</span>')

            renksec.destroy()

    def kategori(self, *_):
        """call category window from kategori"""
        CategoryWindow(self.set_text)
