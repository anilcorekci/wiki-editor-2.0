# -*- coding: utf-8 -*-
#pylint:disable=C0413
"""
Wiki Editor 2010!
"""
import sys
import os
import re

import gi
gi.require_version('GtkSource', '4')
gi.require_version('Gtk', '3.0')

from gi.repository import GtkSource as edit
from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf

from tercihler import ConfigWindow
from buildtool import ToolItem
from custom_button import CustomButton
from wikitext import WikiText

import uyeol as ol

from araclar import (
        LANGS, SIMGELER, TMP_FILE, UI_INFO, HAK, MENUSETUP,
        get_stock, hakkinda, get_filechooser, mesaj, hata,
    )

# referring names from araclar:
#  MENUSETUP,LANGS, SIMGELER, TMP_FILE, UI_INFO, HAK #pix or infos
#  get_stock, hakkinda get_filechooser, mesaj, hata #functions

TARGET_TYPE_URI_LIST = 80
VISIT_PAGE = 'http://wiki.ubuntu-tr.net/index.php/Acemiler_i%C3%A7in_Wiki&'
UNDEFINED = "Kaydedilmemiş"

def get_main_menu(pencere, menu_items):
    """
    return uimanager Menubar
    """
    uimanager = gtk.UIManager()
    action_group = gtk.ActionGroup(name="my_actions")
    action_group.add_actions(menu_items)

    uimanager.add_ui_from_string(UI_INFO)
    uimanager.insert_action_group(action_group)

    accelgroup = uimanager.get_accel_group()
    pencere.add_accel_group(accelgroup)

    return uimanager.get_widget("/MenuBar")

class WikiEditor():
    """
    Kullanılan genel değişkenlerin listesi
    """
    udf_list = {} # undefinded_list

    gl_b = {
        "tab_n_page": None, # current nth page of notebook
        "yol": "/file//path", # file path of wikitext
        "name": None, # file name of wikitext
        "tool_active": gtk.Toolbar,
        "full_screen": None, #top_level window value
        "showy_widgets_": [gtk.Box, gtk.Toolbar, gtk.Menu],
        "label": gtk.Label, # status bar label gives information about langugae
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

        menu_items = [
            ("Dosya", None, "Dosya"),
            ( "Yeni", None,"Yeni", "<control>N", None, lambda _: self.yeni(False)),
            ( "Aç", None,"Aç", "<control>O", None, self.open_file ),
            ( "Kaydet", None, "Kaydet","<control>S", None, self.kayit),
            ( "Farklı Kaydet", None, "Farklı Kaydet","<shift><control>S", None, self.save_as ),

            ( "Yazdır", None, "Yazdır", "<control>Y", None, lambda widget:
                self.notebook.get_nth_page( #get current wikitext from notebook
                    self.gl_b["tab_n_page"]
                ).yazdir( widget, data=self.gl_b["yol"] ) ),

            ( "Çık", None, "Çık", "<control>Q", None, self.soru),
            ( "Düzen", gtk.Action(name="Düzen"), "Düzen"),

            ( "Geri Al", None,"Geri Al", "<control>Z", None, lambda _:
                self.current_buffer.undo() if self.current_buffer.can_undo()
                else self.ileti.set_text( "Bellekte Başka Geri Alınıcak Argüman Yok..")
            ),

            ( "Tekrar Yap", None,"Tekrar Yap", "<shift><control>Z", None, lambda _:
                self.current_buffer.redo() if self.current_buffer.can_redo()
                else self.ileti.set_text( "Bellekte Başka Tekrar Yapılıcak Argüman Yok..")
            ),

            ( "Hizalama", None,"Hizalama" ),
            ( "Sola Hizala",None,"Sola Hizala",None, None, self.set_tool_edit),
            ( "Ortala",None ,"Ortala",None, None, self.set_tool_edit),
            ( "Sağa Hizala",None ,"Sağa Hizala",None, None, self.set_tool_edit),
            ( "Tercihler", None, "Tercihler",  "<control>P",
                 None, lambda _: ConfigWindow(self).show_config ),

            ( "Bul", None, "Bul", "<control>F",None, lambda widget:
                self.notebook.get_nth_page(self.gl_b["tab_n_page"]).arama(widget, False)),

            ( "Görünüm", gtk.Action(name="Görünüm"), "Görünüm" ),
            ( "Sadece Simge", None,"Sadece Simge", None, None, self.set_tool_edit),
            ( "Sadece Metin", None, "Sadece Metin", None, None, self.set_tool_edit),
            ( "Metin ve Simge", None,"Metin ve Simge", None, None, self.set_tool_edit),

            ( "Tam Ekran", None, "Tam Ekran", "F11", None, lambda *_:
              [ self.gl_b.update( {"full_screen": not self.gl_b["full_screen"] } ),
              [ pencere.fullscreen() if self.gl_b["full_screen"]  else pencere.unfullscreen() ], ]
            ),

            ( "Araçlar",gtk.Action(name="Araçlar"), "Araçlar"),
            ( "Boşlukları Kodla", None,"Boşlukları Kodla", "<control>E",None, self.set_tool_edit ),
            ( "Boşlukları Kodlama", None, "Boşlukları Kodlama",
                    "<control><shift>E", None, self.set_tool_edit),

            ( "Wiki Kodlarını Pasifleştir", None,
                    "Wiki Kodlarını Pasifleştir", "<control>W",None, self.set_tool_edit ),

            ( "Wiki Kodlarını Pasifleştirme",None,
                    "Wiki Kodlarını Pasifleştirme","<control><shift>W",None, self.set_tool_edit ),

            ( "Maddele", None, "Maddele", "<control><shift>M", None, self.set_tool_edit ),

            ( "Maddeleme", None, "Maddeleme",
                     "<control><shift>N", None, self.set_tool_edit ),

            ( "Yardım", gtk.Action(name="Yardım"),"Yardım" ),
            ( "İçindekiler", None, "İçindekiler" ,
                    "F1", None, lambda _: os.system(f'xdg-open {VISIT_PAGE}') ),

            ( "Bize Katılın", None, "Bize Katılın", "F2",
                None, lambda _:  ol.Uyeol().main() ),

            ( "Hakkında", None ,"Hakkında",None, None, hakkinda),
        ]

        box = gtk.VBox(False, 0)
        box.show()

        menubar = get_main_menu(pencere, menu_items)
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
        buton = CustomButton(self, LANGS)

        toolbar = gtk.Toolbar()
        toolbar.set_border_width(4)
        self.gl_b["tool_active"] = toolbar

        for item, list_info in SIMGELER.items():
            ToolItem(self, item, *list_info )

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

        hiding_items = [

            ["Yeni",  "Yeni Bir Belge Oluştur",
            get_stock( gtk.STOCK_FILE),
            lambda _: self.yeni(False) ],

            ["Aç",  "Bir Dosya Aç",
            get_stock(gtk.STOCK_OPEN),
            self.open_file ],

            ["Tercihler", "Wiki Editor Tercihleri ",
            get_stock( gtk.STOCK_PREFERENCES),
            lambda _: ConfigWindow(self).show_config],

            ["Üye Ol",
            "Henüz Wikiye Üye Değil Misin ?\nO Zaman Bu Tam Senin İçin ..",
            uye, lambda _: ol.Uyeol().main() ],

            ["Hakkında",
            "Wiki Editor Hakkında",
            HAK, hakkinda ]
        ]

        for item in hiding_items:
            ToolItem(self,*item )

        table = gtk.Table(400,400)
        table.attach(self.notebook, 0, 400, 2, 399)
        table.attach(toolbar, 0, 1, 1, 2)
        table.attach(hide, 0, 4, 0, 4)
        table.attach(box,0, 1, 0, 1)
        table.attach(hbox, 0, 400, 399, 400)

        pencere.add(table)
        pencere.show_all()
        hide.hide()

        self.gl_b["showy_widgets_"] = [ hbox, toolbar, menubar ]


    def switch(self, tab=False, widget= False, tab_n_page=False):
        """print(widget, tab_n_page)
        check file_path and assing to self.gl_b["yol"]
        """
        hbox = tab.get_tab_label(widget)
        label = hbox.get_children()[1]

        self.gl_b["tab_n_page"] = tab_n_page
        self.gl_b["name"] = label.get_text()

        if not os.path.isfile(self.gl_b["yol"]):
            self.gl_b["yol"] = f"{UNDEFINED}:{tab_n_page + 1}"

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
            return None

        return buffer

    @property
    def current_buffer(self):
        """
        return current buffer
        """
        return self.current_editor.get_buffer()

    def yeni(self,yol, baslik=str):
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

        def note_label_box(label_text, yol):
            """
            create Hbox for page title and return
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

        page_title = note_label_box( baslik, yol)

        wiki_text = WikiText(self.ileti, self.statu)

        self.notebook.append_page( wiki_text, page_title)
        self.notebook.show_all()
        self.notebook.next_page()

        ConfigWindow(self).set_ayar(set_up=True)

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
                    dialog.destroy()
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

    def set_text(self, text, insert=None ):
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

    def set_tool_edit(self, widget, komut=None):
        """
        activate on click menu item actions
        """
        for label, label_ed in zip(MENUSETUP["GORUNUM"],MENUSETUP["HIZALAMA"]):

            if label == widget.get_label():
                set_up = getattr(gtk.ToolbarStyle, f'{MENUSETUP["GORUNUM"][label]}' )
                self.gl_b["showy_widgets_"][1].set_style(set_up)
                return False

            if label_ed == widget.get_label():
                set_up = getattr(gtk.Justification, f'{MENUSETUP["HIZALAMA"][label_ed]}' )
                self.current_editor.set_justification(set_up)
                return False
#####  set up text using sed regex
        komut = MENUSETUP["ARACLAR"][widget.get_label()]

        if konu:= self.get_konu():

            with open(TMP_FILE, "w", encoding="utf-8") as dosya:
                dosya.write(konu)

            os.system(komut)

            with open(TMP_FILE, "r", encoding="utf-8") as dosya:
                self.set_text(dosya.read())

            os.system(f"rm -rf {TMP_FILE}" )
        return True

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
            return False

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
                    f"\\nHata Kodu:-2\nHata Mesajı\n:{msj}" )
            return False

        return True

    def open(self, dosya):
        """ open given filepath """
        try:

            with open(dosya, "r", encoding="utf-8" ) as das:
                try:
                    self.set_text( das.read(), True )
                except UnicodeDecodeError as err:
                    hata(f"Hata Kodu:5 \n\tHata Mesajı:{dosya}\
                         \n\tdosyası okunurken hata oluştu!\n{err}\n\n", self)
                    return False

        except IOError as msj:
            hata(f"{dosya}\n\tDosyası Açılamadı\n\
                 \tHata Kodu:-3\n\tHata Mesajı:{msj}\n\n\n", self)
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
