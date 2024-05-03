# -*- coding: utf-8 -*-
#pylint: disable=E0611, C0415
"""
Tools and string variable used in WikiEditor Toplevel
"""
import subprocess as sp_
import gi

from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf
gi.require_version('Gtk', '3.0')

TMP_FILE = "/tmp/wiki-editor"

###Dosya Tipi Seçenekleri############################
langs = {"Düz Metin":"text/plain",
        "C":"text/x-csrc",
        "Css":"text/css",
        ".desktop":"application/x-desktop",
        "Html":"text/html",
        "Glade":"application/x-glade",
        "Python":"text/x-python",
        "Java":"text/x-java",
        "PHP":"application/x-php",
        "Perl":"application/x-perl",
        "Xml":"application/xml",
        "Sh":"application/x-shellscript"}
###Resimler############################pwd
BELGE = "../Simgeler/belge.svg"
#
KAPAT = "../Simgeler/kapat.svg"
#
def resim(yol):
    """
    Retrun gtk Image from given file_path
    """
    image  = gtk.Image()
    image.set_from_file(yol)
    return image

descriptions = {
"Seçilen metin için bold yazı":["'''" ,"'''"],

"Seçilen metin için italik yazı":  ["''" ,"''"] ,

"Seçilen Metin için başlık \n Alt başlık oluşturmak için işlemi tekrarlayın.":  ["==" ,"=="],

"Seçilen Metin için Wiki İç Bağlantısı.":  ["[[" ,"]]"],

"Yazınız için bir renk seçin": "color_select",

"Kırmızı renkte yazmak için":["{{kırmızı|" ,"}} "],

"Mavi renkte yazmak için" : ["{{mavi|" ,"}}  "] ,

"Bir resim seçin ve butona tıklayınn resim şablonu": ["[[Dosya:" ,"]]<br>"],

"Dış bağlantı için wiki şablonu" : ["[" ,"  adres açıklaması]"] ,

"Wiki harici nowiki metin gereksinimi?" : ["<nowiki>" ,"</nowiki>"],

"Komutlar için bir kod şablonu": ["{{kod||<nowiki>" ," </nowiki>}} <br>"],

"Komutlar için uçbirim şablonu" :["{{uçbirim|\n <nowiki>" ,"</nowiki>}}"] ,

"Dosya içerikleri  için wiki şablonu":  ["{{dosya|nerde bu dosya|\n" ,"}}"],

"Yazının Hangi sürüm için olduğunu seçin": ["{{sürüm|" ," }}"] ,

"SUDO alıntıları için bir  şablon":{
# each given glade file must contain label and entry
# each entry and label must be named and enumerated aligned with 1,2,3,4,5.. etc..
# widgets must be in a  window named window1 and box named vbox1
# format text {} refers to each given entry and its corresponding label..

    "../Glade/sudo.glade": "{{{{dergi|sayı={}|tarih={}|sayfano={}|yazar={} }}}}"
    },

"Mozilla Firefox Eklentileri için bir şablon.":{
    "../Glade/firefox.glade": \
    "{{{{firefoxeklentisi|isim={}|ekran_görüntüsü={}|açıklama={}\
|geliştirici={} ||web_sitesi={} }}}}"
},

"Yazılımlar için bir şablon.": {
    "../Glade/yazılım.glade": \
    "{{{{yazılım|isim='{}'|ekran_görüntüsü='{}'|açıklama='{}'\
|geliştirici='{}'|tür='{}'|lisans='{}'|depo='{}'|web_sitesi='{}'}}}}"
},

"Yazınız için bir kategori seçin..": "kategori",
}

simgeler = {}

for simge in sp_.getoutput("ls ../Simgeler").splitlines():
    simge_adi = simge.split(".")[0].split("-")[1]
    for aciklama in descriptions:
        if simge_adi.lower() in aciklama.lower():
            break
    simgeler[simge_adi.title()] = ([
        aciklama.title(),
        resim("../Simgeler/"+simge),
        descriptions[aciklama]
    ])

#############################################################################
HAK = gtk.Image()
HAK.set_from_pixbuf(
    GdkPixbuf.Pixbuf.new_from_file_at_size(
        "wiki-editor.png", 28,28)
    )
###Hakkında####################################################
PROGRAM="Wiki Editor "
#
LOGO ="wiki-editor.png"
#
VERSION="2.0"
#
WHO="copyright© hitokiri"
#
LICENCE="""
Wiki Editor özgür bir yazılımdır, onu Özgür Yazılım
Vakfı'nın yayınladığı GNU Genel Kamu Lisansı'nın 2.
sürümü veya (tercihinize bağlı) daha sonraki sürümleri
altında dağıtabilir ve/veya değiştirebilirsiniz.

Wiki Editor  faydalı olacağı umut edilerek dağıtılmaktadır,
fakat HİÇBİR GARANTİSİ YOKTUR; hatta ÜRÜN DEĞERİ
ya da BİR AMACA UYGUNLUK gibi garantiler de
vermez. Lütfen GNU Genel Kamu Lisansı'nı daha fazla
ayrıntı için inceleyin.
"""
#
MAIL = ["Anıl Çörekcioğlu  <anilcorekci@gmail.com>"]
#
TEAM = r"""
<span foreground="#550085"  size="x-large" font_family="URW Chancery L "><b><u>Wiki Tayfası;</u>

    <i>Ubuntu Türkiye Wiki'sini düzenlemekle ve denetlemekle görevli
    gönüllü insanlardan oluşan bir ekiptir.Ayrıca evrensel Wiki de yer alan
    Türkçe bölümleri de denetleme ve düzenleme yetkisine sahiptirler.
    <span foreground="#642B42"><u>Ubuntu Türkiye Wiki'ye  katkı için tayfa da olunması gerekmemektedir. </u></span>
    <span foreground="#642B42"><u>Katkı yapmak için normal üye olmak yeterlidir,</u></span>düzenleme ve denetleme gibi
    sorumluluk gerektiren,özen isteyen işleri Wiki tayfası üstlenmiştir. </i></b> </span>
    """

##Kategoriler####################################
#
kategoriler= {
"temel": ["Temel Bilgiler","Açık Kaynak Ünlüleri","Kurulum","Nasıl Belgeleri",
    "Sss","Temel Açık Kaynak Bilgileri","Temel Bilgisayar Bilgileri",
    "Temel İnternet Bilgileri","Önemli İnternet Siteleri",
    "Temel Linux Bilgileri","Ubuntu Kaynakları "],
#
"donanim" : ["Donanım", "Ağ kartları", "Grafik", "Grafik Kartları",
    "Monitörler", "Masaüstü Bilgisayarlar",
    "Netbook Bilgisayarlar", "Notebook Bilgisayarlar",
    "Ses Kartları", "Usb Aygıtlar", "Tv Kartları",
    "Yazıcı-Tarayıcı", "İşlemci-ram", "Diğer Donanımlar"],
#
"yazilim": [ "Yazılım", "Ağ","Diğer Yazılımlar", "Donatılar",
    "Dosya Sistemleri", "Grafik Yazılımları", "Güvenlik",
    "İnternet Yazılımları", "İşletim Sistemleri", "Diğer Linux Dağıtımları",
    "Linux Mint", "Masaüstü","Görsellik", "Masaüstü Yöneticileri",
    "Microsoft Windows Yazılımları", "Ofis Yazılımları", "Oyun",
    "Programlama", "Programlama Dilleri",
    "Sanallaştırma", "Ses ve Video Yazılımları",
    "Sistem Uygulamaları", "Sunucu Uygulamaları"],
#
"ubuntu": ["Ubuntu", "Ubuntu Sürümleri", "Paylaşım",
           "Tayfa", "Tayfa Toplantıları",
           "Ubuntu Hakkında", "Ubuntu Türevleri",
           "SUDO Alıntıları", "Ekran Görüntüleri"],
}

####################################################
NO = r'''sed -i -e 's_>_<nowiki>></nowiki>_g' {}
sed -i -e 's_#_<nowiki>#</nowiki>_g' {}
sed -i -e 's_=_<nowiki>=</nowiki>_g' {}
sed -i -e 's_*_<nowiki>*</nowiki>_g' {}
sed -i -e 's_}}_<nowiki>}}</nowiki>_g' {}
sed -i -e 's_{{_<nowiki>{{</nowiki>_g' {}
sed -i -e 's_|_<nowiki>|</nowiki>_g' {}
sed -i -e 's_\[_<nowiki>[</nowiki>_g' {}
sed -i -e 's_]_<nowiki>]</nowiki>_g' {}
sed -i -e 's_~_<nowiki>~</nowiki>_g' {}'''.format(*[TMP_FILE]*10)
####################################################
RNO = r'''sed -i -e 's_<nowiki>__g' {}
sed -i -e 's_</nowiki>__g' {}'''.format(*[TMP_FILE]*2)
####################################################
BOSLUK = r'''sed -i -e 's_ _\&nbsp;_g' {};
sed -i -e 's_    _\&nbsp;\&nbsp;\&nbsp;\&nbsp;_g' {};
sed -i -e 's_    __g' {};
a=`sed "s/$/<br>/" {} > /tmp/wiki`
cat /tmp/wiki > {}
rm -rf /tmp/wiki '''.format(*[TMP_FILE]*5)
####################################################
RBOSLUK = r"""sed -i -e 's_\&nbsp;_ _g' {};
sed -i -e 's_<br>__g' {}""".format(*[TMP_FILE]*2)
####################################################
MADDE = f"""sed -i 's/^/*/' {TMP_FILE}"""
####################################################
RMADDE = f"""sed -i -e 's_*__g' {TMP_FILE}"""
####################################################

menu_setup = {
    "ARACLAR":{
    "Wiki Kodlarını Pasifleştir": NO,
    "Wiki Kodlarını Pasifleştirme": RNO,
    "Maddele": MADDE, "Maddeleme": RMADDE,
    "Boşlukları Kodla": BOSLUK, "Boşlukları Kodlama": RBOSLUK,
    },

    "GORUNUM":
    {"Simge" : "ICONS",
      "Metin" : "TEXT",
    "ve":"BOTH"},

    "HIZALAMA":
    {"Sola Hizala": "LEFT",
      "Ortala": "CENTER",
    "Sağa Hizala": "RIGHT"},
}

################UI INFO MENU AŞAMALARI######################################
UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='Dosya'>
      <menuitem action='Yeni' />
      <menuitem action='Aç' />
      <menuitem action='Kaydet' />
      <menuitem action='Farklı Kaydet' />
      <menuitem action='Yazdır' />
      <menuitem action='Çık' />
    </menu>
    <menu action='Düzen'>
      <menuitem action='Geri Al' />
      <menuitem action='Tekrar Yap' />
      <menu action='Hizalama'>
        <menuitem action='Sola Hizala' />
        <menuitem action='Ortala' />
        <menuitem action='Sağa Hizala' />
      </menu>
      <menuitem action='Bul' />
      <menuitem action='Tercihler' />
    </menu>
    <menu action='Görünüm'>
      <menuitem action='Sadece Metin' />
      <menuitem action='Sadece Simge' />
      <menuitem action='Metin ve Simge' />
      <menuitem action='Tam Ekran' />
    </menu>    
    <menu action='Araçlar'>
      <menuitem action='Boşlukları Kodla' />
      <menuitem action='Boşlukları Kodlama' />
      <menuitem action='Wiki Kodlarını Pasifleştir' />
      <menuitem action='Wiki Kodlarını Pasifleştirme' />
      <menuitem action='Maddele' />
      <menuitem action='Maddeleme' />
    </menu>
    <menu action='Yardım'>
      <menuitem action='İçindekiler' />
      <menuitem action='Bize Katılın' />
      <menuitem action='Hakkında' />
    </menu>
  </menubar>
</ui>
"""

SHORTCUT = """
<control>N        Yeni bir pencere açmak için,
<control>O        Bir metin belgesi açmak için,
<control>S        Yapılan değişiklikleri kayıt etmek için,
<control>F        Kelime grubunda arama yapmak için,
<control>Q        Programdan çıkmak için,

<control>Z          Geri Al,
<shift><control>Z       Tekrar Yap,
<control>P        Tercihler,
                
<control>F1             Temsili Görünüm,

<control>E        Boşlukları Kodla ,
<control><shift>E       Boşlukları Kodlama ,
<control>W        Wiki Kodlarını Pasifleştir ,
<control><shift>W    Wiki Kodlarını Pasifleştirme,
<control><shift>M    Maddele,
<control><shift>N    Maddeleme,

F11        Tam Ekran Moduna Geçmek için,
F1        İçindekiler sayfasına gitmek için,
"""
def hakkinda(*_):
    """
    About Window
    """
    about = gtk.AboutDialog()
    about.set_title(PROGRAM)
    about.set_program_name(PROGRAM)
    about.set_version(VERSION)
    about.set_copyright(WHO)
    about.set_icon_from_file(LOGO)
    about.set_license(LICENCE)
    about.set_authors(MAIL)
    about.set_logo(
        GdkPixbuf.Pixbuf.new_from_file_at_size(
            LOGO, 148, 148)
        )

    about.show_all()
    if about.run() == gtk.ResponseType.CANCEL or gtk.ResponseType.CLOSE:
        about.destroy()

def get_stock(stock_):
    """
    returns stock image from given stock_name
    """
    image_ = gtk.Image()
    image_.set_from_stock( stock_, 1)
    return image_

def get_filechooser(desc_, type_="OPEN"):
    """
    Returns response and dialog
    shows filechooser
    """
    dialog = gtk.FileChooserDialog(
        desc_,None,
        getattr(gtk.FileChooserAction,type_),
        (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
        getattr(gtk, f"STOCK_{type_}"), gtk.ResponseType.OK)
        )

    dialog.set_default_response(gtk.ResponseType.OK)
    dialog.set_icon_from_file("wiki-editor.png")
    filter_ = gtk.FileFilter()
    filter_.set_name("Tüm Dosyalar")
    filter_.add_pattern("*")
    txt = gtk.FileFilter()
    txt.set_name("txt")
    txt.add_pattern("*txt")
    dialog.add_filter(filter_)
    dialog.add_filter(txt)
    response = dialog.run()
    return response, dialog

def mesaj(msj):
    """
    run a message dialog for given text
    """
    dialog = gtk.MessageDialog(
        type=gtk.MessageType.INFO,
        buttons=gtk.ButtonsType.OK )
    dialog.set_markup(msj)
    dialog.show()

    if dialog.run() == gtk.ResponseType.OK:
        dialog.destroy()

def hata(msj):
    """
    returns custom error message for wikitext
    """
    from __main__ import HITO as notebook
    buffer = notebook.current_buffer
    pixbuf =  GdkPixbuf.Pixbuf.new_from_file_at_size("gtk-cancel.png",128,128)
    iter_ = buffer.get_iter_at_offset(0)
    buffer.insert(iter_, "\n\n")
    buffer.insert_pixbuf(iter_, pixbuf)
    buffer.insert(iter_, msj)
    tag = buffer.create_tag( foreground="black",
                paragraph_background="#7F3731",
                right_margin=0,
                indent=50,
                left_margin=0,
                size_points=15.0,
                wrap_mode=gtk.WrapMode.WORD )
    start, end = buffer.get_bounds()
    buffer.apply_tag(tag, start, end)
    notebook.current_editor.set_editable(False)
    notebook.current_editor.set_border_window_size(gtk.TextWindowType.LEFT, 0)
    buffer.set_modified(False)
