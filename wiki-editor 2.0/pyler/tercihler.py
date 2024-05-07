# -*- coding: utf-8 -*-
"""
build and open preferences
"""
import os
import sqlite3
from ast import literal_eval

from gi.repository import Gtk as gtk
from gi.repository import Pango as pango
from araclar import LICENCE, SHORTCUT, mesaj

WIKI_DB = os.environ['HOME']+"/.wiki_editor.db"

WRAP = {
    1:["WORD", gtk.RadioButton, False],
    2:["CHAR",gtk.RadioButton, True],
    3:["NONE",gtk.RadioButton, False]
}

SET = {
    "font_spin": None, #spin button for tab indent
    "yazi": None, #gtk fontbutton for tercihler window
    "show_number":None, #show number for wikitext
    "modify_font":None,
    "yazitipi": None, # current font preference
    "activated": None, #whether open a blank page or not
}

class ConfigWindow(gtk.Builder):
    """
    Build glade file
    """
    def __init__(self, wikieditor):
        gtk.Builder.__init__(self)

        self.notebook = wikieditor.notebook

        if self.notebook.get_n_pages() < 1:
            wikieditor.yeni(False)
            SET["activated"] = True

        self.wiki = wikieditor.current_editor
        self.current_buffer = wikieditor.current_buffer
        self.gl_b = wikieditor.gl_b

    @property
    def show_config(self, *_):
        """
        Show configuration window
        """

        self.notebook.show()

        if SET["activated"] is True:
            self.current_buffer.set_text(f"{LICENCE}\n{SHORTCUT}")
            self.current_buffer.set_undo_manager()
            self.current_buffer.set_modified(False)
            SET["activated"] = not SET["activated"]

        self.add_from_file("../Glade/tercihler.glade")
        vbox = self.get_object("hbuttonbox1")
        pencere = self.get_object("window1")

        pencere.connect("delete_event", lambda x:
            [ x.destroy(), self.set_ayar() ] )

        kapat, yar = gtk.Button("Kapat"), gtk.Button("Yardım")

        kapat.connect("clicked", lambda *_:
            [ pencere.destroy(), self.set_ayar() ] )

        yar.connect("clicked", lambda _:
            mesaj("Biri Buna Basar Demiştim Zaten...\n" +
            """Yardım Almak İçin <a href= "http://www.ubuntu-tr.net\" >Ubuntu Türkiye</a> """)
            )

        vbox.add(yar)
        vbox.add(kapat)

        data = self.set_ayar(True)

        SET["font_spin"] = self.get_object("spinbutton1")

        SET["font_spin"].connect("value_changed",  lambda x:
            self.wiki.set_tab_width( int( f'{x.get_value().strip("0.") }' ) ) )

        SET["font_spin"].set_value( float( data["sekme"][0] ) )

        SET["yazi"] = self.get_object("fontbutton1")
        SET["yazi"].set_font_name( data["font"][0] )

        SET["yazi"].connect("font-set", lambda _:
            self.wiki.modify_font( SET["yazi"].get_font_desc() ) )

        SET["show_number"] = self.get_object("checkbutton1")

        SET["show_number"].connect( "toggled", lambda x:
            self.wiki.set_show_line_numbers( x.get_active() ) )

        SET["show_number"].set_active(literal_eval(data["sekmeleri_say"][0] ))

        hide_widget = self.gl_b["showy_widgets_"][0]

        self.get_object("checkbutton3").connect("clicked", lambda x:
            hide_widget.hide() if x.get_active()
            else hide_widget.show() )

        SET["modify_font"] = self.get_object("checkbutton2")
        SET["modify_font"].connect("toggled", self.set_font)

        SET["modify_font"].set_active( literal_eval(data["yazi_tipi"][0]) )

        for add in range(1,4):
            WRAP[add][1] = self.get_object(f"radiobutton{add}")
            WRAP[add][1].connect("clicked", self.radio_wrap)
            WRAP[add][2] = False

            if WRAP[add][0] == data["wrap_mode"][0]:
                WRAP[add][1].set_active(True)

        pencere.show_all()

    def radio_wrap(self, *_):
        """
        adjust wrap_mode for wikitext
        """
        for item in WRAP.values():
            item[2] = False
            try:
                if item[1].get_active():
                    self.wiki.set_wrap_mode(
                        getattr(gtk.WrapMode, item[0]) )
                    item[2]  = True
            except TypeError:
                pass

    def set_font(self, *_):
        """
        set font for wikitext
        """
        if SET["modify_font"].get_active():
            self.wiki.modify_font(None)
        else:
            SET["yazitipi"] = SET["yazi"].get_font_desc()
            self.wiki.modify_font( SET["yazitipi"] )

    def set_ayar(self, data=False, set_up=False):
        """
        write configs to wiki.db
        """
        if not os.path.isfile(WIKI_DB):
            os.system(f"cp wiki_editor.db {WIKI_DB}")

        con = sqlite3.connect(WIKI_DB)
        cur = con.cursor()

# Retrun sql data as a dictionary##
        if data is not False:
            cur.execute('SELECT preference, value FROM settings')
            ans = dict(cur.fetchall()) #; print(ans)
            #split "|" and convert key item as a list
            return {key: ans[key].split("|") for key in ans}

#############################################
        # set_up data from wiki.db
        if set_up is True:
            data = self.set_ayar(True)

            for settings in sorted(data):
                set_value_as, set_value = data[settings]

                match settings:
                    case "wrap_mode":
                        getattr(self.wiki, set_value) \
                            (getattr(gtk.WrapMode, set_value_as))

                    case "font":
                        SET["yazitipi"] = pango.FontDescription(set_value_as)
                        getattr(self.wiki, set_value) \
                            ( SET["yazitipi"] )

                    case "yazi_tipi":
                        if literal_eval(set_value_as) is True:
                            getattr(self.wiki, set_value)(None)

                    case "sekme":
                        getattr(self.wiki, set_value) \
                            ( int( set_value_as.strip(".0") ) )

                    case "sekmeleri_say":
                        getattr(self.wiki, set_value) \
                            ( literal_eval(set_value_as) )

            return False

        ###### update data from ui input ###############

        data = {
            "sekme": [
                f"{ SET['font_spin'].get_value() }",
                "set_tab_width"
                ],

            "font": [
                f"{ SET['yazi'].get_font_name() }",
                "modify_font"
                ],

            "yazi_tipi": [
                f"{ SET['modify_font'].get_active() }",
                "modify_font"
                ],

            "sekmeleri_say": [
                f"{ SET['show_number'].get_active() }",
                "set_show_line_numbers"
                ],

            "wrap_mode": [
                [ wrap_[0] for wrap_ in WRAP.values() if wrap_[2] ] [0],
                'set_wrap_mode'
                ],
            }

        # Write the data in wiki-editor.db file

        for preference, list_  in data.items():
            set_value, set_value_as = list_
            cur.execute(
                f"UPDATE settings SET value='{set_value}|{set_value_as}'" +
                f"WHERE preference='{preference}'"
            )

        con.commit()
        self.set_ayar(set_up=True)
        return True
