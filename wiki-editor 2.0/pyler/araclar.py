#!/usr/bin/env python
# -*- coding: utf-8 -*-  
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk 
from gi.repository import GdkPixbuf
import subprocess as sp_

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
belge =  "../Simgeler/belge.svg"
#
kapat =  "../Simgeler/kapat.svg"
#
def resim(yol):
	resim  = gtk.Image()
	resim.set_from_file(yol)
	return resim


descriptions = {
"Seçilen metin için bold yazı":["'''" ,"'''"],
"Seçilen metin için italik yazı":  ["''" ,"''"] ,
"Seçilen Metin için başlık \n Alt başlık oluşturmak için işlemi tekrarlayın.":  ["==" ,"=="],
"Seçilen Metin için Wiki İç Bağlantısı.":  ["[[" ,"]]"],
"Yazınız için bir renk seçin": "anonim",
"Kırmızı renkte yazmak için":["{{kırmızı|" ,"}} "],
"Mavi renkte yazmak için" : ["{{mavi|" ,"}}  "] ,
"Bir resim seçin ve butona tıklayınn resim şablonu": ["[[Dosya:" ,"]]<br>"],
"Dış bağlantı için wiki şablonu" : ["[" ,"  adres açıklaması]"] ,
"Wiki harici nowiki metin gereksinimi?" : ["<nowiki>" ,"</nowiki>"],
"Komutlar için bir kod şablonu": ["{{kod||<nowiki>" ," </nowiki>}} <br>"],
"Komutlar için uçbirim şablonu" :["{{uçbirim|\n <nowiki>" ,"</nowiki>}}"] ,
"Dosya içerikleri  için wiki şablonu":  ["{{dosya|nerde bu dosya|\n" ,"}}"], 
"Yazının Hangi sürüm için olduğunu seçin": ["{{sürüm|" ," }}"] ,
"SUDO alıntıları için bir  şablon": "sudo",
"Mozilla Firefox Eklentileri için bir şablon.": "eklenti",
"Yazılımlar için bir şablon.": "yazilim",
"Yazınız için bir kategori seçin..": "kategori",
}

simgeler = {}

for simge in sp_.getoutput("ls ../Simgeler").splitlines():
	simge_adi = simge.split(".")[0].split("-")[1]
	for aciklama in descriptions:
		if simge_adi.lower() in aciklama.lower():
			break
	simgeler[simge_adi.title()] = ([aciklama.title(), resim("../Simgeler/"+simge), descriptions[aciklama]])


#############################################################################
hak = gtk.Image()
pix = GdkPixbuf.Pixbuf.new_from_file_at_size("wiki-editor.png",28,28)	
hak.set_from_pixbuf(pix)	
###Hakkında####################################################
program="Wiki Editor "
#
versiyon="2.0"
#
kim="copyright© hitokiri"
#
lisans="""
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
mail=["Anıl Çörekcioğlu  <anilcorekci@gmail.com>"]
#
tayfa = """
<span foreground="#550085"  size="x-large" font_family="URW Chancery L "><b><u>Wiki Tayfası;</u> 

	<i>Ubuntu Türkiye Wiki'sini düzenlemekle ve denetlemekle görevli
	gönüllü insanlardan oluşan bir ekiptir.Ayrıca evrensel Wiki de yer alan 
	Türkçe bölümleri de denetleme ve düzenleme yetkisine sahiptirler.  
	<span foreground="#642B42"  ><u>Ubuntu Türkiye Wiki'ye  katkı için tayfa da olunması gerekmemektedir. </u></span>
	<span foreground="#642B42"  ><u>Katkı yapmak için normal üye olmak yeterlidir,</u></span>düzenleme ve denetleme gibi
	sorumluluk gerektiren,özen isteyen işleri Wiki tayfası üstlenmiştir. </i></b> </span>		
	"""

##Kategoriler####################################
#
kategoriler= {
"temel": ["Temel Bilgiler","Açık Kaynak Ünlüleri","Kurulum","Nasıl Belgeleri",
    "Sss","Temel Açık Kaynak Bilgileri","Temel Bilgisayar Bilgileri","Temel İnternet Bilgileri",
    "Önemli İnternet Siteleri" ,"Temel Linux Bilgileri","Ubuntu Kaynakları "] ,
#
"donanim" : ["Donanım","Ağ kartları","Grafik","Grafik Kartları","Monitörler","Masaüstü Bilgisayarlar",
    "Netbook Bilgisayarlar","Notebook Bilgisayarlar","Ses Kartları","Usb Aygıtlar","Tv Kartları","Yazıcı-Tarayıcı","İşlemci-ram","Diğer Donanımlar"],
#
"yazilim": [ "Yazılım","Ağ","Diğer Yazılımlar","Donatılar","Dosya Sistemleri","Grafik Yazılımları","Güvenlik",
    "İnternet Yazılımları","İşletim Sistemleri","Diğer Linux Dağıtımları","Linux Mint","Masaüstü","Görsellik","Masaüstü Yöneticileri",
    "Microsoft Windows Yazılımları","Ofis Yazılımları","Oyun","Programlama","Programlama Dilleri",
    "Sanallaştırma","Ses ve Video Yazılımları","Sistem Uygulamaları","Sunucu Uygulamaları"],
#	
"ubuntu": ["Ubuntu","Ubuntu Sürümleri","Paylaşım","Tayfa","Tayfa Toplantıları" ,"Ubuntu Hakkında","Ubuntu Türevleri","SUDO Alıntıları","Ekran Görüntüleri"],
}

####################################################
no = """sed -i -e 's_>_<nowiki>></nowiki>_g' /tmp/wiki-editor		
sed -i -e 's_#_<nowiki>#</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_=_<nowiki>=</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_*_<nowiki>*</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_}_<nowiki>}</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_{_<nowiki>{</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_|_<nowiki>|</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_\[_<nowiki>[</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_]_<nowiki>]</nowiki>_g' /tmp/wiki-editor
sed -i -e 's_~_<nowiki>~</nowiki>_g' /tmp/wiki-editor"""
####################################################
rno = """sed -i -e 's_<nowiki>__g' /tmp/wiki-editor		
sed -i -e 's_</nowiki>__g' /tmp/wiki-editor"""
####################################################
bosluk = """sed -i -e 's_ _\&nbsp;_g' /tmp/wiki-editor ;
sed -i -e 's_	_\&nbsp;\&nbsp;\&nbsp;\&nbsp;_g' /tmp/wiki-editor ;
sed -i -e 's_	__g' /tmp/wiki-editor ;
a=`sed "s/$/<br>/" /tmp/wiki-editor > /tmp/wiki`
cat /tmp/wiki > /tmp/wiki-editor """
####################################################
rbosluk = """sed -i -e 's_\&nbsp;_ _g' /tmp/wiki-editor;
sed -i -e 's_<br>__g' /tmp/wiki-editor"""
####################################################
madde = """a=`sed 's/^/*/' /tmp/wiki-editor|tee /tmp/wiki`
echo "$a"  > /tmp/wiki-editor
sed -i -e 's_\&_\&#38;_g' /tmp/wiki
sed -i -e 's_<_\&#60;_g' /tmp/wiki
sed -i -e 's_}_\&#125;_g' /tmp/wiki
sed -i -e 's_{_\&#123;_g' /tmp/wiki
b=`sed "s/$/\<\/li\>/" /tmp/wiki`
echo  "<body xmlns='http://www.w3.org/1999/xhtml'>\n    <ul >"  > /tmp/madde
echo "$b" >> /tmp/madde 
sed -i -e "s_*_      <li>_g" /tmp/madde
echo "    </ul>\n</body>" >> /tmp/madde  """
####################################################
rmadde = "sed -i -e 's_*__g' /tmp/wiki-editor"
####################################################
def hakkinda(w=False):
	hakkinda = gtk.AboutDialog()	
	hakkinda.set_title("Wiki Editor ")
	hakkinda.set_program_name(program)
	hakkinda.set_version(versiyon) 
	hakkinda.set_copyright(kim)
	hakkinda.set_icon_from_file("wiki-editor.png")
	hakkinda.set_license(lisans)
	hakkinda.set_authors(mail)
	logo = GdkPixbuf.Pixbuf.new_from_file_at_size("wiki-editor.png", 148, 148)
	hakkinda.set_logo(logo)	
	
	hakkinda.show_all()
	if  hakkinda.run() == gtk.ResponseType.CANCEL or gtk.ResponseType.CLOSE:
		hakkinda.destroy()

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


ksayol="""
<control>N		Yeni bir pencere açmak için,
<control>O		Bir metin belgesi açmak için,
<control>S		Yapılan değişiklikleri kayıt etmek için,
<control>F		Kelime grubunda arama yapmak için,
<control>Q		Programdan çıkmak için

<control>Z  		Geri Al,          
<shift><control>Z       Tekrar Yap,
<control>P		Tercihler,      
                
<control>F1             Temsili Görünüm, 

<control>E		Boşlukları Kodla ,
<control><shift>E       Boşlukları Kodlama ,
<control>W		Wiki Kodlarını Pasifleştir ,  
<control><shift>W	Wiki Kodlarını Pasifleştirme,
<control><shift>M	Maddele,
<control><shift>N	Maddeleme, 

F11		Tam Ekran Moduna Geçmek için,
F1		İçindekiler sayfasına gitmek için,
"""