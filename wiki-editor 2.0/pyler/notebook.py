# -*- coding: utf-8 -*-
#pylint: disable=consider-using-f-string
#pylint: disable=C0413, R0904
"""
Wiki Editor 2010!
"""
import sys
from ast import literal_eval
import os
import re
import sqlite3

import gi
gi.require_version('GtkSource', '4')

from gi.repository import GtkSource as edit
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GdkPixbuf
from gi.repository import Pango as pango

import wikitext as wiki
import uyeol as ol

import araclar as ar
from araclar import menu_setup
from araclar import get_stock
from araclar import get_filechooser
from araclar import mesaj
from araclar import hata


TARGET_TYPE_URI_LIST = 80
WIKI_DB = os.environ['HOME']+"/.wiki_editor.db"
UI_INFO = ar.UI_INFO
SIMGELER = ar.simgeler
VISIT_PAGE = 'http://wiki.ubuntu-tr.net/index.php/Acemiler_i%C3%A7in_Wiki&'
TMP_FILE = ar.TMP_FILE
UNDEFINED = "Kaydedilmemiş"

class WikiEditor():
    """
    Kullanılan genel değişkenlerin listesi
    """
    udf_list = {} # undefinded_list

    gl_b = {
        "tab_n_page": None, # current nth page of notebook
        "yol": "/file//path", # file path of wikitext
        "name": None, # file name of wikitext
        "pencere": None, # always equal to the active page that shown
        "yazitipi": None, # current font preference
        "wrap_mode": {1:["WORD"], 2:["CHAR"], 3:["NONE"]},
        # current choosen wrap mode for wikitext
        "radio": {}, # give list of radio button in relation to categories window
        "full_screen": None, #top_level window value
        "label": gtk.Label, # status bar label gives information about langugae
        "font_spin": None, "showy_widgets_": [gtk.Box, gtk.Toolbar, gtk.Menu],
        "yazi": None, #gtk fontbutton for tercihler window
        "show_number": None,  "modify_font": None,  "tool_active": gtk.Toolbar,
        "lang_manager": edit.LanguageManager(),
    }

    def __init__(self):
        """
        Menu and widget build on gtk window
        add window actions and tools
        """
        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect("switch-page", self.switch)

        pencere = gtk.Window()
        pencere.connect("delete_event", self.soru)
        pencere.set_title(" Wiki Editor")
        pencere.set_icon_from_file("wiki-editor.png")
        pencere.resize(780,580)

        self.menu_items = [
            ("Dosya", None, "Dosya"),
            ( "Yeni", None,"Yeni", "<control>N", None, lambda _: self.yeni(False)),
            ( "Aç", None,"Aç", "<control>O", None, self.open_file ),
            ( "Kaydet", None, "Kaydet","<control>S", None, self.kayit),
            ( "Farklı Kaydet", None, "Farklı Kaydet","<shift><control>S", None, self.save_as ),
            ( "Yazdır", None, "Yazdır", "<control>Y", None, self.yazdir),
            ( "Çık", None, "Çık", "<control>Q", None, self.soru),
            ( "Düzen", gtk.Action(name = "Düzen"), "Düzen"),
            ( "Geri Al", None,"Geri Al", "<control>Z", None, self.geri ),
            ( "Tekrar Yap", None,"Tekrar Yap", "<shift><control>Z", None, self.tekrar_yap),
            ( "Hizalama", None,"Hizalama" ),
            ( "Sola Hizala",None,"Sola Hizala",None, None, self.set_tool_edit),
            ( "Ortala",None ,"Ortala",None, None, self.set_tool_edit),
            ( "Sağa Hizala",None ,"Sağa Hizala",None, None, self.set_tool_edit),
            ( "Tercihler", None, "Tercihler",  "<control>P", None, self.tercihler),
            ( "Bul", None, "Bul", "<control>F",None, self.arama),
            ( "Görünüm", gtk.Action(name = "Görünüm"), "Görünüm" ),
            ( "Sadece Simge", None,"Sadece Simge", None, None, self.set_tool_edit),
            ( "Sadece Metin", None, "Sadece Metin", None, None, self.set_tool_edit),
            ( "Metin ve Simge", None,"Metin ve Simge", None, None, self.set_tool_edit),
            ( "Tam Ekran", None, "Tam Ekran", "F11", None, self.change_screen ),
            ( "Araçlar",gtk.Action(name = "Araçlar"), "Araçlar"),
            ( "Boşlukları Kodla", None,"Boşlukları Kodla", "<control>E",None, self.sed_setup ),
            ( "Boşlukları Kodlama", None, "Boşlukları Kodlama",
                    "<control><shift>E", None, self.sed_setup),
            ( "Wiki Kodlarını Pasifleştir", None,
                    "Wiki Kodlarını Pasifleştir", "<control>W",None, self.sed_setup ),
            ( "Wiki Kodlarını Pasifleştirme",None,
                    "Wiki Kodlarını Pasifleştirme","<control><shift>W",None, self.sed_setup ),
            ( "Maddele", None, "Maddele", "<control><shift>M", None, self.sed_setup ),
            ( "Maddeleme", None, "Maddeleme",
                     "<control><shift>N", None, self.sed_setup ),
            ( "Yardım", gtk.Action(name = "Yardım"),"Yardım" ),
            ( "İçindekiler", None, "İçindekiler" ,
                    "F1", None, lambda _: os.system(f'xdg-open {VISIT_PAGE}') ),
            ( "Bize Katılın", None, "Bize Katılın", "F2", None, lambda _:  ol.Uyeol().main() ),
            ( "Hakkında", None ,"Hakkında",None, None, ar.hakkinda),
        ]

        box = gtk.VBox(False, 0)
        box.show()

        menubar = self.get_main_menu(pencere)
        box.pack_start( menubar, False, True, 0)
        menubar.show()

################ variable can be passed too.####################################
#        wiki.ileti = self.ileti
#        wiki.statu = self.statu
####################################################
        self.statu = gtk.Statusbar()
        self.statu.set_size_request(150,10)
        self.ileti = gtk.Label()
############
        hbox = gtk.HBox()
        buton = self.menu(ar.langs)
        toolbar = self.toolmake()

        hbox.pack_start(self.ileti,True,False,0)
        hbox.pack_end(buton,False,True,30)
        hbox.pack_start(self.statu,False,True,0)

        hide = gtk.Toolbar()
##################################################
        self.gl_b["tool_active"] = hide
    #    toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
    #    toolbar.set_style(gtk.TOOLBAR_BOTH)
        hide.set_border_width(4)

        uye = gtk.Image()
        pix = GdkPixbuf.Pixbuf.new_from_file_at_size("üye.png",28,28)
        uye.set_from_pixbuf(pix)

        self.toolitem("Yeni","Yeni Bir Belge Oluştur",
                get_stock( gtk.STOCK_FILE),
                lambda _: self.yeni(False))
        self.toolitem( "Aç",   "Bir Dosya Aç",
                get_stock(gtk.STOCK_OPEN),
                self.open_file )
        self.toolitem( "Tercihler", "Wiki Editor Tercihleri ",
                get_stock( gtk.STOCK_PREFERENCES),
                self.tercihler )
        self.toolitem( "Üye Ol",
                "Henüz Wikiye Üye Değil Misin ?\nO Zaman Bu Tam Senin İçin ..",
                uye, lambda _: ol.Uyeol().main() )

        self.toolitem( "Hakkında",
                "Wiki Editor Hakkında",
                ar.HAK, ar.hakkinda )

        table = gtk.Table(400,400)
        table.attach(self.notebook, 0, 400, 2, 399)
        table.attach(toolbar, 0, 1, 1, 2)
        table.attach(hide, 0, 4, 0, 4)
        table.attach(box,0, 1, 0, 1)
        table.attach(hbox, 0, 400, 399, 400)

        pencere.add(table)
        pencere.show_all()
        hide.hide()
        self.pen = pencere
        self.gl_b["showy_widgets_"] = [ hbox, toolbar, menubar ]

    def get_main_menu(self, pencere):
        """
        return uimanager Menubar
        """
        uimanager = gtk.UIManager()
        action_group = gtk.ActionGroup(name="my_actions")
        action_group.add_actions(self.menu_items)

        uimanager.add_ui_from_string(UI_INFO)
        uimanager.insert_action_group(action_group)

        accelgroup = uimanager.get_accel_group()
        pencere.add_accel_group(accelgroup)

        return uimanager.get_widget("/MenuBar")

    def switch(self, tab = False, widget = False, tab_n_page= False):
        """print(widget, tab_n_page)
        check file_path and assing to self.gl_b["yol"]
        """
        self.gl_b["tab_n_page"] = tab_n_page
        hbox = tab.get_tab_label(widget)
        label = hbox.get_children()[1]
        self.gl_b["name"] = label.get_text()
        text = label.get_tooltip_text()
        yol = text.split(":")[1]

        if os.path.isfile(yol):
            self.gl_b["yol"] = yol
        else:
            self.gl_b["yol"] = f"{yol}:{tab_n_page + 1}"

    @property
    def current_editor(self):
        """
        return current editor
        """
        page = self.notebook.get_current_page()
        scroll_w = self.notebook.get_nth_page(page)
        try:
            buffer = scroll_w.get_widget()
            buffer.set_left_margin(8)

        except AttributeError:
            buffer = None
        return buffer

    @property
    def current_buffer(self):
        """
        return current buffer
        """
        return self.current_editor.get_buffer()

    def menu(self, item_list):
        """
        create menu item and return button widget
        """
        menu = gtk.Menu()
        for each in item_list:
            menu_items = gtk.MenuItem(each)
            menu.append(menu_items)
            menu_items.connect("activate", self.menuitem_response, each)
            menu_items.show()

        ekleme = gtk.HBox()
        image = get_stock(gtk.STOCK_GO_DOWN)
        label = gtk.Label("Düz Metin")
        ekleme.pack_start(label,False,False,10)
        ekleme.pack_start(image,False,False,0)
        self.gl_b["label"] = label

        def button_press( widget, event):
            """
            button press action for STATU the custom button
            """
        #    print(widget, event.type)
            if event.type == gdk.EventType.BUTTON_PRESS:
        #        if event.button == 1:
                widget.popup(None, None, None, event.button, event.time, event.time)

        buton = gtk.Button()
        buton.set_relief(gtk.ReliefStyle.NONE)
        buton.connect_object("event", button_press, menu)
        buton.add(ekleme)
        buton.show()
        return buton

    def menuitem_response(self, _, string):
        """
        change custom button label text
        """
        self.gl_b["label"].set_text(f"{string}")
        self.change()

    def toolmake(self):
        """
        self.toolitem("İtalik",   #Alt Metin
        "Seçilen metin için italik yazı", #Balon Metin
        ar.italikresim,
        #Resim gtk.Image / eklemek için araclar.py--> ismi = resim("dosya_yolu")
        ) #Buton için görev liste ise seçilen metin
        için başına sonuna eklenecekler liste içinde "başı","sonu"
        # liste değilse doğruda görev olarak çağırılacak..."""

        toolbar = gtk.Toolbar()
        self.gl_b["tool_active"] = toolbar
        toolbar.set_border_width(4)

        for item, list_info in SIMGELER.items():
            self.toolitem(item, *list_info )

        return toolbar

    def toolitem(self, label, tooltip, resim, islem):
        """
        create tooltiem via getting args
        """
        item = gtk.ToolButton(resim, label)
        item.set_tooltip_text(tooltip)
        item.set_label(label)
        item.set_icon_widget(resim)

        type_of_islem = type(islem)

        if type_of_islem is dict:
        # if islem is dict unpack dict and call self.sablon
            file_path, format_ = list( i for i in islem.items() )[0]
            item.connect('clicked', lambda _: self.sablon(file_path, format_))
        elif type_of_islem is list:
        # if islem is list send it to self.selection_
            item.connect('clicked',lambda _: self.selection_(islem[0], islem[1]) )
        # if it's a string call it as a fuction within hitokiri...
        elif type_of_islem is str:
            item.connect('clicked', getattr(self, islem))
        # if it's a fuction leave it as it is...
        else:
            item.connect('clicked',islem )

        item.show()
        self.gl_b["tool_active"].insert(item, -1)

    def change(self, *_):
        """
        change current language of wikieditor
        """
    #    self.current_editor().get_buffer().set_data('languages-manager', lm)
#        manager = self.current_editor().get_buffer().get_data('languages-manager')
        tip = self.gl_b["label"].get_text()
        lang = ar.langs[tip]
        language = self.gl_b["lang_manager"].guess_language(content_type=lang)
        self.current_buffer.set_language(language)

    def yeni(self,yol, baslik = "yok"):
        """
        create new tab with wikitext
        """
        page_number = self.notebook.get_current_page() + 2

        if not yol:
            baslik = f"{UNDEFINED} Belge: {page_number}"
            yol = baslik
            # IF UNDEFINED NAME EXIST IN NOTEBOOK...
            if yol in [ self.udf_list[n] for n in self.udf_list]:
                #DEFINE NEW UNDEFINED AS +1 FROM THE CURRENT MAX NUMBER IN THE LIST
                page_number = max(
                    [ int( self.udf_list[n].split(":")\
                    [1]) for n in self.udf_list ]
                ) + 1
                baslik = f"{UNDEFINED} Belge: {page_number}"

            self.udf_list[int(page_number)] = baslik

        else:
            baslik = yol
            for i in re.findall(".*?../", baslik):
                baslik=baslik.replace(i, "")

        page_title = self.note_label_box( baslik, yol)
        wiki_text = wiki.WikiEditor()

        self.notebook.append_page( wiki_text, page_title)
        self.notebook.show_all()
        self.notebook.next_page()

        self.set_ayar(set_up = True)

    def kapat(self, _, label_text):
        """
        close operation for both tab and toplevel window
        """
        i = -1

        while self.notebook.get_n_pages():

            i += 1
            self.notebook.set_current_page(i)

            get_n_widget = self.notebook.get_nth_page(i)
            # return wiki_editor
            get_n_widget = self.notebook.get_tab_label(get_n_widget)
            # return box
            get_n_info = get_n_widget.get_children()[1].get_text()
            # return box child list_ #image#label/button

            if label_text != get_n_info:
                continue

            # if get_n_info in self.udf_list
            if get_n_info in [ self.udf_list[n] for n in self.udf_list]:
            #    print(get_n_info)
            #    self.udf_list.pop(i+1)
                #REMOVE get_n_info from self.udf_list, REDUCE -1 each given index
                self.udf_list = {key-1: val for key, val in self.udf_list.items() if key != i+1 }
                # REDEFINE index info from 1 to N large from UNDEFINED INFO
                self.udf_list = {key: self.udf_list[val] for key, val in \
                                  zip(range(1,len(self.udf_list)+1), self.udf_list ) }
            #    print(self.udf_list)

            response_ = None

            if self.current_buffer.get_modified():
                dialog = gtk.MessageDialog(type = gtk.MessageType.WARNING)
                dialog.add_button("Kaydetmeden Kapat", gtk.ResponseType.NO)
                dialog.add_button("İptal", gtk.ResponseType.CANCEL)
                dialog.add_button("Kaydet", gtk.ResponseType.OK)

                dialog.set_markup("<b>Kapatmadan önce <tt>'"+ label_text + \
                    "'</tt> \nbelgesinde yaptığınız değişiklikleri kaydetmek ister misiniz?" +
                    "</b>\n\n<i>Kaydetmediğiniz takdirde," +
                    " yaptığınız son değişiklikler kaybolacak.</i>")

                dialog.show()
                response_ = dialog.run()

                if response_ == gtk.ResponseType.OK:
                    self.kayit(self.gl_b["name"], True)
                    break
                if response_ == gtk.ResponseType.CANCEL:
                    dialog.destroy()
                    return False

                dialog.destroy()

            self.notebook.remove_page(i)
            break

        if self.notebook.get_n_pages() == 0:
            self.gl_b["tool_active"].show()
            for hide in self.gl_b["showy_widgets_"]:
                hide.hide()

    def note_label_box(self, label_text, yol):
        """
        create Hbox and return it
        """
        if self.notebook.get_n_pages() == 0:
            self.gl_b["tool_active"].hide()
            for show in self.gl_b["showy_widgets_"]:
                show.show()

        box1 = gtk.HBox()
        image = get_stock(gtk.STOCK_CLOSE)
        image1 = get_stock(gtk.STOCK_FILE)
        box1.add(image1)

        label = gtk.Label(label_text)
        box1.add(label)
        label.set_tooltip_text(f"Dosya yolu: {yol}")

        buton = gtk.Button()
        buton.add(image)
        buton.set_relief(gtk.ReliefStyle.NONE)
        buton.set_tooltip_text("Belgeyi Kapat" )
        buton.set_size_request(24, 24)
        buton.connect("clicked", self.kapat, label_text)
        self.gl_b["yol"] = yol
        box1.add(buton)
        box1.show_all()
        return box1

    def geri(self, *_):
        """
        undo action for buffer
        """
        if self.current_buffer.can_undo():
            self.current_buffer.undo()
        else:
            self.ileti.set_text( "Bellekte Başka Geri Alınıcak Argüman Yok..")

    def tekrar_yap(self, *_):
        """
        redo action for buffer
        """
        if self.current_buffer.can_redo():
            self.current_buffer.redo()
        else:
            self.ileti.set_text( "Bellekte Başka Tekrar Yapılıcak Argüman Yok..")

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
        range_ = [ [1, range_], [range_, range_*2]]

        for en_, lb_ in zip(range(*range_[0]), range(*range_[1]) ):
            dict_[en_] =  builder.get_object("entry"+str(en_))
            dict_[lb_] =  builder.get_object("label"+str(en_))

        ekle = gtk.Button(" Tamam ")
        ekle.connect("clicked", lambda _: self.set_en_label_text(dict_,range_,format_))
        vbox.add(ekle)

        self.gl_b["pencere"] = pencere
        pencere.show_all()

    def set_en_label_text(self, dict_,range_, format_):
        """
        order and apply actions for custom glade files
        """
        get_text = []
        for en_, lb_ in zip(range(*range_[0]), range(*range_[1]) ):
            if not dict_[en_].get_text():
                mesaj(f"{ dict_[lb_].get_text() }\nBoş bırakılmamalı!")
                return False
            get_text.append(dict_[en_].get_text())

        self.set_text(format_.format(*get_text), True)
        self.gl_b["pencere"].destroy()
        return True

    def kategori(self, *_):
        """
        build, create and show categoreis
        """
        pencere = gtk.Window()
        pencere.set_size_request(400,-1)
        pencere.set_modal(True)
        pencere.set_resizable(False)
        pencere.set_title("Yazınız İçin Kategori")
        pencere.set_icon_from_file("../Simgeler/Z-kategori.png")
        box = gtk.VBox()

        bilgi = { }

        for kategori, order in zip(ar.kategoriler,range(1, len(ar.kategoriler)+1)):
            bil = gtk.ListStore(str)
            bilg = gtk.ComboBox.new_with_model(bil)

            for liste_ in ar.kategoriler[kategori]:
                bil.append([liste_])

            rt1 = gtk.CellRendererText()
            bilg.pack_start(rt1, True)
            bilg.add_attribute(rt1, "text", 0)
            bilg.set_active(0)
            box.add(bilg)
            bilgi[order] = bilg

        hbox = gtk.VBox()

        for order in range( 1, len(bilgi) + 1 ):
            if order == 1:
                self.gl_b["radio"][order] = gtk.RadioButton( None, None )
            else:
                self.gl_b["radio"]= gtk.RadioButton.new_from_widget(
                                        self.gl_b["radio"][order-1]
                                    )

            hbox.add(self.gl_b["radio"][order])

        dume = gtk.Button("Tamam")
        dume.connect("clicked", lambda _: self.radio_clicked(bilgi))

        kutu = gtk.Table(4, 4)
        kutu.set_border_width(12)
        kutu.set_col_spacings(8)
        kutu.set_row_spacings(10)
        kutu.attach(hbox, 0, 1, 1, 2)
        kutu.attach(box, 1, 2, 1, 2)
        kutu.attach(dume, 0, 4, 3, 4)
        pencere.add(kutu)
        pencere.show_all()
        self.gl_b["pencere"] = pencere

    def arama(self, widget, *_):
        """
        open search dialog
        """
        wiki_text = self.notebook.get_nth_page(self.gl_b["tab_n_page"])
        wiki_text.arama(widget, False)

    def tercihler(self, *_):
        """
        build and open preferences
        """
        self.notebook.show()
        if self.notebook.get_n_pages() < 1:
            self.yeni(False)
            self.current_buffer.set_text(f"{ar.LICENCE}\n{ar.SHORTCUT}")
            self.current_buffer.set_undo_manager()
            self.current_buffer.set_modified(False)

        builder = gtk.Builder()
        builder.add_from_file("../Glade/tercihler.glade")
        vbox = builder.get_object("hbuttonbox1")
        pencere = builder.get_object("window1")

        pencere.connect("delete_event",
                lambda *x: [x[0].destroy(),self.set_ayar() ]
            )

        data = self.set_ayar(True)

        kapat, yar = gtk.Button("Kapat"), gtk.Button("Yardım")

        yar.connect("clicked",
            lambda _: mesaj("Biri Buna Basar Demiştim Zaten...\n" +
                """Yardım Almak İçin <a href= "http://www.ubuntu-tr.net\" >Ubuntu Türkiye</a> """)
            )

        vbox.add(yar)
        vbox.add(kapat)

        kapat.connect("clicked", lambda *x:
                [ pencere.destroy(), self.set_ayar() ]
            )

        font_spin = builder.get_object("spinbutton1")
        font_spin.connect( "value_changed", lambda *x:
                    self.current_editor.set_tab_width(
                    int( f'{x[0].get_value().strip("0.")}')
                )  )

        font_spin.set_value(float(data["sekme"][0] ) )
        self.gl_b["font_spin"] = font_spin

        yazi = builder.get_object("fontbutton1")
        yazi.set_font_name(data["font"][0])
        yazi.connect("font-set",
                lambda _: self.current_editor.modify_font(yazi.get_font_desc())
            )
        self.gl_b["yazi"] = yazi

        show_number =  builder.get_object("checkbutton1")
        show_number.connect( "toggled",
                lambda x: self.current_editor.set_show_line_numbers(x.get_active() )
            )
        show_number.set_active(literal_eval(data["sekmeleri_say"][0] ))
        self.gl_b["show_number"] = show_number

        status_box = builder.get_object("checkbutton3")
        status_box.connect("clicked", lambda x:
            self.gl_b["showy_widgets_"][0].hide() if x.get_active()\
                  else self.gl_b["showy_widgets_"][0].show() )

        modify_font =  builder.get_object("checkbutton2")
        modify_font.connect("toggled",self.yazil)
        modify_font.set_active(literal_eval(data["yazi_tipi"][0] ))
        self.gl_b["modify_font"] = modify_font

        for add in range(1,4):
            self.gl_b["wrap_mode"][add].extend([
                    builder.get_object(f"radiobutton{add}"),
                    False]
                )

            self.gl_b["wrap_mode"][add][1].connect("clicked",self.radio_wrap)

            if self.gl_b["wrap_mode"][add][0] == data["wrap_mode"][0]:
                self.gl_b["wrap_mode"][add][1].set_active(True)

        self.gl_b["pencere"] = pencere
        pencere.show_all()

    def yazil(self, *_):
        """
        set font for wikitext
        """
        if self.gl_b["modify_font"].get_active() is True:
            self.current_editor.modify_font(None)
        else:
            self.gl_b["yazitipi"] =  self.gl_b["yazi"].get_font_desc()
            self.current_editor.modify_font( self.gl_b["yazitipi"] )

    def radio_wrap(self, selected_ = False):
        """
        adjust wrap_mode for wikitext
        """
        for radio, item in self.gl_b["wrap_mode"].items():

            self.gl_b["wrap_mode"][radio][2] = item[1].get_active()

            if item[1].get_active():
                if selected_ is True:
                    return item[0]
                self.current_editor.set_wrap_mode(getattr(gtk.WrapMode, item[0]))
                break
        return None
        #    print(self.wrap_mode[radio])

    def open_file(self, _):
        """
        open new file from path
        """
        response, dialog = get_filechooser("Okumak ve değiştirmek için bir doysa seç..")

        if response == gtk.ResponseType.OK:
            bilgi = dialog.get_filename()
            self.yeni(bilgi)
            self.open(bilgi)

        dialog.destroy()

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
            ans = {key: ans[key].split("|") for key in ans} #;print(ans)
            return ans

#########################################
        # Write the data in wiki-editor.db file
#############################################
        # set_up data from wiki.db
        if set_up is True:
            data = self.set_ayar(True)

            for settings in sorted(data):
                set_value_as, set_value = data[settings]

                if  settings == "wrap_mode":
                    getattr(self.current_editor, set_value) (getattr(gtk.WrapMode, set_value_as))

                elif settings == "font":
                    self.gl_b["yazitipi"]  = pango.FontDescription(set_value_as)
                    getattr(self.current_editor, set_value)( self.gl_b["yazitipi"] )

                elif settings == "yazi_tipi" and literal_eval(set_value_as) is True:
                    getattr(self.current_editor, set_value)(None)

                elif "sekme" == settings:
                    getattr(self.current_editor, set_value) (int(set_value_as.split(".0")[0]))

                elif "sekmeleri_say" == settings:
                    getattr(self.current_editor, set_value) (literal_eval(set_value_as))

            return False
        ###### update data from ui input ###############
        wrap_mode = self.radio_wrap(True)

        data = {
            "sekme": [ f"{ self.gl_b['font_spin'].get_value() }", "set_tab_width"],
            "font": [ f"{ self.gl_b['yazi'].get_font_name() }", "modify_font"],
            "yazi_tipi": [ f"{ self.gl_b['modify_font'].get_active()}", "modify_font"],
            "sekmeleri_say": [ f"{self.gl_b['show_number'].get_active()}", "set_show_line_numbers"],
            "wrap_mode":[wrap_mode, 'set_wrap_mode'],
            }

        for preference, list_  in data.items():
            set_value, set_value_as = list_
            cur.execute("UPDATE  settings SET value='%s|%s' WHERE preference='%s'" \
                        % (set_value,set_value_as,preference) )

        con.commit()
        self.set_ayar(set_up=True)
        return True

    def save_as(self, *_):
        """
        save wikitext as file
        """
        response, dialog = get_filechooser("Değişikliklerle Birlikte Metni Kaydet..","SAVE")

        if response == gtk.ResponseType.OK:
            bilgi = dialog.get_filename()
            konu = self.get_konu(True)

            try:
                with open(bilgi ,"w", encoding="utf-8") as dosya:
                    dosya.write(konu)
                    page = self.notebook.get_current_page()
                    self.notebook.remove_page(page)
                    self.yeni(bilgi)
                    self.open(bilgi)
            except IOError as msj:
                mesaj(f"{bilgi}\nDosyası Kayıt Edilemedi..\nHata Kodu:-1\nHata Mesajı:{msj}")

        dialog.destroy()

    def set_text(self, text, insert = None ):
        """
        set current buffer text
        """
        self.current_buffer.begin_user_action()
        if insert:
            self.current_buffer.insert_at_cursor(text)
        else:
            start, end = self.current_buffer.get_selection_bounds()
            self.current_buffer.delete(start, end)
            self.current_buffer.insert_at_cursor(text)
        self.current_buffer.end_user_action()

    def selection_(self, head_, tail_ ):
        """
        set and change selection of text
        """
        konu = self.get_konu()

        if self.current_editor and konu:
            self.set_text(head_ + konu + tail_)
            return True

        self.ileti.set_text("Seçili hiç bir metin yok !")
        return None

    def get_konu(self, all_text=False):
        """
        return selection of text
        """
        if all_text is True:
            start, end = self.current_buffer.get_bounds()
            konu = self.current_buffer.get_slice(start, end,1)
            return konu

        if bounds:=self.current_buffer.get_selection_bounds():
            start, end = bounds
            konu = self.current_buffer.get_slice(start, end,1)
            return konu

        self.ileti.set_text("Seçili hiç bir metin yok !")
        return False

    def color_select(self, *_):
        """
        build and show color selection apply to text with <span color>
        """
        if konu:= self.get_konu():
            renksec = gtk.ColorSelectionDialog("Bir renk seçin")
            renksec.set_icon_from_file("../Simgeler/07-renk seç.png")
            renksec.show()

            if renksec.run() == gtk.ResponseType.OK:
                renk = renksec.get_color_selection().get_current_color().to_floats()
                # crazy stuff here needs to change rgb01 to rgb250
                self.set_text('<span style="color:rgb({}, {}, {} );">{}</span>'.\
                                format( *[i*255 for i in renk],konu))

            renksec.destroy()

    def radio_clicked(self, bilgi):
        """
        insert action for categories window
        """
        for number in self.gl_b["radio"]:
            if self.gl_b["radio"][number].get_active():
                iter_ = bilgi[number].get_active_iter()
                model = bilgi[number].get_model()
                konu = model[iter_][0]
                self.set_text(f"[[kategori:{konu}]]", True)

        self.gl_b["pencere"].destroy()

    def sed_setup(self, widget, komut = None):
        """
        set up text using sed regex
        """
        komut = menu_setup["ARACLAR"][widget.get_label()]

        if konu:= self.get_konu():

            with open(TMP_FILE, "w", encoding="utf-8") as dosya:
                dosya.write(konu)

            os.system(komut)

            with open(TMP_FILE, "r", encoding="utf-8") as dosya:
                self.set_text(dosya.read())

            os.system(f"rm -rf {TMP_FILE}" )

    def set_tool_edit(self, widget, *_):
        """
        activate on click menu item actions
        """
        for label, label_ed in zip(menu_setup["GORUNUM"],menu_setup["HIZALAMA"]):

            if label in widget.get_label():
                set_up = getattr(gtk.ToolbarStyle, f'{menu_setup["GORUNUM"][label]}' )
                self.gl_b["showy_widgets_"][1].set_style(set_up)

            elif label_ed in widget.get_label():
                set_up = getattr(gtk.Justification, f'{menu_setup["HIZALAMA"][label_ed]}' )
                self.current_editor.set_justification(set_up)

    def change_screen(self, *_):
        """
        change screen size full_screen = not full_screen
        """
        self.gl_b["full_screen"] = not self.gl_b["full_screen"]

        if self.gl_b["full_screen"]:
            self.pen.fullscreen()
        else:
            self.pen.unfullscreen()

    def soru(self, *_):
        """
        ask and close toplevel window
        """
        i = -1

        while True:
            i += 1
            self.notebook.set_current_page(i)

            if  self.notebook.get_n_pages() < i:
                sys.exit(0)

            elif self.current_editor:

                if self.current_buffer.get_modified():
                    soru = gtk.MessageDialog(type = gtk.MessageType.QUESTION,
                                             buttons = gtk.ButtonsType.YES_NO)

                    soru.set_markup("<b>Kayıt Edilmemiş Değişiklikler Var </b>" +
                     "\n<i>Yine de Programdan çıkmak istediğinize emin misiniz?</i>")

                    if soru.run() == gtk.ResponseType.YES:
                        soru.destroy()
                        sys.exit(1)
                    else:
                        soru.destroy()
                        gtk.main()

            else: sys.exit(0)

    def kayit(self, *_):
        """
        save current buffer file
        """
        if UNDEFINED in self.gl_b["yol"]:
            self.save_as()
        else:
            konu = self.get_konu(True)

            try:
                with open( self.gl_b["yol"], "w", encoding="utf-8") as dosya:
                    dosya.write(konu)
                    self.ileti.set_text(
                            f"'{ self.gl_b['yol'] }' dosyası kayıt edildi.."
                        )
                    self.current_buffer.set_modified(False)

            except IOError as msj:
                mesaj(f"{self.gl_b['yol']}\nDosyası Kayıt Edilemedi.." + \
                      f"\\nHata Kodu:-2\nHata Mesajı:{msj}" )

    def yazdir(self, widget, *_):
        """ call print operation from wikitext  """
        page = self.notebook.get_current_page()
        wiki_text = self.notebook.get_nth_page(page)
        wiki_text.yazdir(widget, data = self.gl_b["yol"] )

    def open(self, dosya):
        """ open given filepath """
        try:

            with open(dosya, "r", encoding="utf-8" ) as das:
                try:
                    self.set_text( das.read(), True )
                except UnicodeDecodeError as err:
                    hata(f"Hata Kodu:5 \n\tHata Mesajı:{dosya}\
                         \n\tdosyası okunurken hata oluştu!\n{err}\n\n")
                    return False

        except IOError as msj:
            hata(f"{dosya}\n\tDosyası Açılamadı\n\
                 \tHata Kodu:-3\n\tHata Mesajı:{msj}\n\n\n")
            return False

        language = self.gl_b["lang_manager"].guess_language(dosya)

        try:
            lang_name = language.get_mime_types()[0]
            lang_name = re.sub(".*.-", "", lang_name)
            self.gl_b["label"].set_text(lang_name)
        except AttributeError:
            self.gl_b["label"].set_text("Düz Metin")

        self.current_buffer.set_language(language)
        self.current_buffer.set_undo_manager()
        self.current_buffer.set_modified(False)
        return True
