# -*- coding: utf-8 -*-
#pylint: disable=C0413, E1101
"""
kategori referring from araclar.py in notebook
"""

from gi.repository import Gtk as gtk
from araclar import CATEG

class CategoryWindow(gtk.Window):
    """
        build, create and show categoreis
    """
    radio = {} # give list of radio button in relation to categories window

    def __init__(self, set_text):

        gtk.Window.__init__(self)
        self.set_text = set_text

        self.set_size_request(400,-1)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_title("Yazınız İçin Kategori")
        self.set_icon_from_file("../Simgeler/Z-kategori.png")
        box = gtk.VBox()

        bilgi = {}

        for kategori, order in zip( CATEG, range( 1, len(CATEG) + 1 ) ):
            bil = gtk.ListStore(str)
            bilg = gtk.ComboBox.new_with_model(bil)
            bilgi[order] = bilg

            for liste_ in CATEG[kategori]:
                bil.append([liste_])

            rt1 = gtk.CellRendererText()
            bilg.pack_start(rt1, True)
            bilg.add_attribute(rt1, "text", 0)
            bilg.set_active(0)
            box.add(bilg)

        hbox = gtk.VBox()

        for order in range( 1, len( bilgi ) + 1 ):
            if order == 1:
                self.radio[order] = gtk.RadioButton( None, None )
            else:
                self.radio[order] = gtk.RadioButton.\
                        new_from_widget( self.radio[order - 1] )

            hbox.add( self.radio[ order ] )

        dume = gtk.Button( "Tamam" )
        dume.connect( "clicked", lambda _: self.radio_clicked( bilgi ) )

        kutu = gtk.Table( 4, 4 )
        kutu.set_border_width( 12 )
        kutu.set_col_spacings( 8 )
        kutu.set_row_spacings( 10 )

        kutu.attach( hbox, 0, 1, 1, 2)
        kutu.attach( box, 1, 2, 1, 2)
        kutu.attach( dume, 0, 4, 3, 4)

        self.add( kutu )
        self.show_all()

    def radio_clicked(self, bilgi):
        """
        insert choosen into wikitext
        """
        for number, radio in self.radio.items():
            if radio.get_active():
                iter_ = bilgi[number].get_active_iter()
                model = bilgi[number].get_model()
                konu = model[iter_][0]
                self.set_text(f"[[kategori:{konu}]]", True)

        self.destroy()
