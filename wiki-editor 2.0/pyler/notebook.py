# -*- coding: utf-8 -*-     
import gi
gi.require_version('GtkSource', '4')
from gi.repository import GObject as gobject
from gi.repository import GtkSource as edit
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk 
from gi.repository import GdkPixbuf
from gi.repository import Pango as pango

import os, urllib,re,sys #pango
import sqlite3
TARGET_TYPE_URI_LIST = 80
import araclar as ar
import wikitext as wiki
import uyeol as ol


wiki_db = os.environ['HOME']+"/.wiki_editor.db"

UI_INFO = ar.UI_INFO

class hitokiri(object):
	def get_main_menu(self, pencere):
		uimanager = gtk.UIManager()
		action_group = gtk.ActionGroup(name="my_actions" )
		action_group.add_actions(self.menu_items)

        # Throws exception if something went wrong
		uimanager.add_ui_from_string(UI_INFO)
		uimanager.insert_action_group(action_group)


        # Add the accelerator group to the toplevel window
		accelgroup = uimanager.get_accel_group()
		pencere.add_accel_group(accelgroup)


		return uimanager.get_widget("/MenuBar")

	def __init__(self):
		self.i = -1
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
			( "Yeni",  None,"Yeni",   "<control>N", None, self.yeni),
			( "Aç",    None,"Aç",  "<control>O", None, self.ac ),     
			( "Kaydet",  None, "Kaydet","<control>S", None, self.kayit),
			( "Farklı Kaydet",  None, "Farklı Kaydet","<shift><control>S", None, self.tasi ),
            ( "Yazdır", None, "Yazdır", "<control>Y", None, self.yazdir),     
            ( "Çık", None, "Çık", "<control>Q", None, self.soru),
			( "Düzen", gtk.Action(name="Düzen"), "Düzen"),
			( "Geri Al", None,"Geri Al",  "<control>Z", None, self.geri ),          
			( "Tekrar Yap", None,"Tekrar Yap", "<shift><control>Z", None, self.rgeri),
			( "Hizalama", None,"Hizalama" ),   
			( "Sola Hizala",None,"Sola Hizala",None, None, self.deger),
			( "Ortala",None ,"Ortala",None, None, self.deger),                  
			( "Sağa Hizala",None ,"Sağa Hizala",None, None, self.deger),      
			( "Tercihler", None, "Tercihler",  "<control>P", None, self.tercihler),      
			( "Bul", None, "Bul", "<control>F",None, self.arama),     
			( "Görünüm", gtk.Action(name="Görünüm"), "Görünüm" ),
			( "Sadece Simge",   None,"Sadece Simge",  None, None, self.set_tool),
			( "Sadece Metin",  None, "Sadece Metin", None, None, self.set_tool),
			( "Metin ve Simge", None,"Metin ve Simge", None, None, self.set_tool),             
			( "Tam Ekran",  None, "Tam Ekran", "F11", None, self.tam ),     
			( "Araçlar",gtk.Action(name="Araçlar"), "Araçlar"),            
			( "Boşlukları Kodla", None,"Boşlukları Kodla", "<control>E",None, self.bosluk ),
			( "Boşlukları Kodlama", None, "Boşlukları Kodlama", "<control><shift>E", None, self.bosluk),
			( "Wiki Kodlarını Pasifleştir", None,"Wiki Kodlarını Pasifleştir",  "<control>W",None, self.nooo ),	    
			( "Wiki Kodlarını Pasifleştirme",None, "Wiki Kodlarını Pasifleştirme","<control><shift>W",None, self.nooo ),
			( "Maddele", None, "Maddele",  "<control><shift>M", None, self.madde ),
			( "Maddeleme", None, "Maddeleme", "<control><shift>N", None, self.madde ),	   			
			( "Yardım", gtk.Action(name="Yardım"),"Yardım" ),
			( "İçindekiler", None, "İçindekiler" , "F1", None, self.kurulum),
			( "Bize Katılın", None, "Bize Katılın", "F2", None, self.katil ),	    
			( "Hakkında", None ,"Hakkında",None, None, ar.hakkinda),
			]  

		box = gtk.VBox(False, 0)
		box.show()
		
		self.menubar = self.get_main_menu(pencere)
		box.pack_start(self.menubar, False, True, 0)
		self.menubar.show()
			
		self.toolbar = self.toolmake()		
		self.statu = gtk.Statusbar()  
		self.statu.set_size_request(150,10)
		self.hbox = gtk.HBox()
		self.buton =  self.menu(ar.langs) 
		self.ileti = gtk.Label()

####################################################
		wiki.ileti = self.ileti
		wiki.statu = self.statu
####################################################

		self.hbox.pack_start(self.ileti,True,False,0)
		self.hbox.pack_end(self.buton,False,True,30)
		self.hbox.pack_start(self.statu,False,True,0)

		frame = gtk.Frame( )
		self.note = gtk.Notebook()
		self.hide = self.hidetool()

		frame.add(self.note)
		self.paned = gtk.VPaned()

		self.paned.pack1(self.notebook, resize=False, shrink=False)
		table = gtk.Table(400,400)
		table.attach( self.paned,0,400,2,399)
		table.attach(self.toolbar,0,1,1,2)
		table.attach(self.hide,0,4,0,4)
		table.attach(box,0,1,0,1)
		table.attach(self.hbox,0,400,399,400)

		pencere.add(table)
		pencere.show_all()	
		self.hide.hide()
		self.pen = pencere 
		self.full_screen = None
		self.lm = edit.LanguageManager()

	def switch(self, tab=False, widget=False, tab_N=False):
	#	print(widget, tab_N)
		self.tab_N = tab_N
		hbox = tab.get_tab_label(widget)
		label = hbox.get_children()[1]
		self.name = label.get_text()
		text = label.get_tooltip_text()
		yol = text.split(":")[1]

		if os.path.isfile(yol):
			self.yol = text.split(":")[1]
			return False
		self.yol = text.split(":")[1] + text.split(":")[2]

	#	print(self.yol)

	def editor(self):
		page = self.notebook.get_current_page()
		sw = self.notebook.get_nth_page(page)
		try:
			buffer = sw.get_widget() 
	#		print (buffer)
		except AttributeError:
			buffer = None	
		return buffer
	def menu(self,item):
		self.menu = gtk.Menu()
		for x in item:
			menu_items = gtk.MenuItem(x)   
			self.menu.append(menu_items)
	#		print(x)
			menu_items.connect("activate", self.menuitem_response, x)
			menu_items.show()
			ek = self.resim_label_box(False,"Düz Metin")
		buton = gtk.Button()
		buton.set_relief(gtk.ReliefStyle.NONE)
		buton.connect_object("event", self.button_press, self.menu)
		buton.add(ek)
		buton.show()
		return buton
	def resim_label_box(self, resim_filename, label_text):
		box1 = gtk.HBox()
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_GO_DOWN,1)
		self.label = gtk.Label(label_text)
		box1.pack_start(self.label,False,False,10)
		box1.pack_start(image,False,False,0)
		box1.show_all()
		return box1
	def button_press(self, widget, event):
	#	print(widget, event.type)
		if event.type == gdk.EventType.BUTTON_PRESS:
	#		if event.button == 1:
			widget.popup(None, None, None, event.button, event.time, event.time)
			return True
		return False
	def menuitem_response(self, widget, string):
		self.lang= "%s" % string
		self.label.set_text(self.lang)
		self.change(1) 

	def hidetool(self):
		toolbar = gtk.Toolbar()
		self.tool_active = toolbar
	#	toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
	#	toolbar.set_style(gtk.TOOLBAR_BOTH)
		toolbar.set_border_width(4)
		yeni = gtk.Image()
		yeni.set_from_stock(gtk.STOCK_FILE,1)
		ac = gtk.Image()
		ac.set_from_stock( gtk.STOCK_OPEN,1)
		ci = gtk.Image()
		ci.set_from_stock( gtk.STOCK_PREFERENCES,1)
 
		uye = gtk.Image() 
		pix = GdkPixbuf.Pixbuf.new_from_file_at_size("üye.png",28,28)	
		uye.set_from_pixbuf(pix)	
		self.toolitem("Yeni","Yeni Bir Belge Oluştur", yeni, self.yeni) 
		self.toolitem( "Aç",   "Bir Dosya Aç",ac,self.ac )     
		self.toolitem( "Tercihler",   "Wiki Editor Tercihleri ",ci,self.tercihler )      
		self.toolitem( "Üye Ol",   "Henüz Wikiye Üye Değil Misin ?\nO Zaman Bu Tam Senin İçin ..",uye,self.katil )      
		self.toolitem( "Hakkında",   "Wiki Editor Hakkında",ar.hak,ar.hakkinda )      
		return  toolbar

	def toolmake(self):
		toolbar = gtk.Toolbar()
		#toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
	#	toolbar.set_style(True)
		self.tool_active = toolbar

		toolbar.set_border_width(4)
	#	self.toolitem(
	#			"İtalik",   #Alt Metin
	#			"Seçilen metin için italik yazı", #Balon Metin 
	#			ar.italikresim,		#Resim gtk.Image / eklemek için araclar.py--> ismi = resim("dosya_yolu")
	#			)      #Buton için görev liste ise seçilen metin için başına sonuna eklenecekler liste içinde "başı","sonu"
									# liste değilse doğruda görev olarak çağırılacak...
		
		for item in ar.simgeler:
			self.toolitem(item, ar.simgeler[item][0], ar.simgeler[item][1],ar.simgeler[item][2])

		return toolbar  

	def toolitem(self, label, tooltip,resim,islem):
		item = gtk.ToolButton(resim, label)
		item.set_tooltip_text(tooltip)
		item.set_label(label)
		item.set_icon_widget(resim)

		if type(islem) is list:
			item.connect('clicked',lambda x: self.secim(islem[0], islem[1]) )
		elif type(islem) is str:
			item.connect('clicked', getattr(self,islem))
		else:
			item.connect('clicked',islem )
		
		item.show()
		self.tool_active.insert(item, -1) 

	def change(self,data):
	#	self.editor().get_buffer().set_data('languages-manager', lm)
#		manager = self.editor().get_buffer().get_data('languages-manager')
		tip = self.label.get_text()
		lang = ar.langs[tip]
		language = self.lm.guess_language(content_type=lang)
		self.editor().get_buffer().set_language(language) 	
	#	self.editor().set_buffer(self.editor().get_buffer())
		
	def sek(self,me,baslik,yol):
		self.i +=1
		i = str(self.i+1)
		if not baslik and not yol:
			baslik = "Kaydedilmemiş Belge: " + i
			yol =  "Kaydedilmemiş Belge: "  + i 
		else:	
			grep=re.findall(".*?../", baslik)
			for i in grep:
				baslik=baslik.replace(i, "")
			

		merhaba = self.note_label_box( '../Simgeler/kapat.svg',baslik,yol)
		buf = wiki.wikieditor()
		self.notebook.insert_page( buf,merhaba,1)
		self.notebook.show_all()
		self.notebook.next_page()
		self.ayarlar()

	def kapat(self,w,yol,label_text):
     
		if self.i < 0: return False

		else: self.i-=1

		while self.notebook.get_n_pages():

			self.notebook.set_current_page(self.tab_N)

			no = True

			if self.editor().get_buffer().get_modified():
				dialog = gtk.MessageDialog(type=gtk.MessageType.WARNING)
				dialog.add_button("Kaydetmeden Kapat",gtk.ResponseType.NO)
				dialog.add_button("İptal",gtk.ResponseType.CANCEL)
				dialog.add_button("Kaydet",gtk.ResponseType.OK)
				dialog.set_markup("<b>Kapatmadan önce <tt>'"+ label_text +"'</tt> \nbelgesinde yaptığınız değişiklikleri kaydetmek ister misiniz?"+\
        							"</b>\n\n<i>Kaydetmediğiniz takdirde, yaptığınız son değişiklikler kaybolacak.</i>")
				dialog.show()
				ne = dialog.run() 
				if ne ==  gtk.ResponseType.OK:
					self.kayit(self.name,1)
					no = None
				elif ne ==  gtk.ResponseType.CANCEL:
					no = None
					dialog.destroy()
					self.i+=1
					break
				dialog.destroy()
			if no:
				self.notebook.remove_page(self.tab_N)	
				break

		if self.notebook.get_n_pages() == 0:
			self.hbox.hide(),self.toolbar.hide(),self.menubar.hide(),self.hide.show()
			self.notebook.remove_page(0)	

	def note_label_box(self, resim_filename, label_text,yol):

		if self.notebook.get_n_pages()  == 0:
			self.hbox.show(),self.toolbar.show(),self.menubar.show(), self.hide.hide()

		box1 = gtk.HBox()
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_CLOSE,1)
		image1 = gtk.Image()
		image1.set_from_stock(gtk.STOCK_FILE,1)	
		box1.add(image1)
		label = gtk.Label(label_text)
		box1.add(label)
		label.set_tooltip_text("Dosya yolu:" + str(yol))
		buton = gtk.Button()
		buton.add(image)
		buton.set_relief(gtk.ReliefStyle.NONE)
		buton.set_tooltip_text("Belgeyi Kapat" )	
		buton.set_size_request(24,24)
		buton.connect("clicked",self.kapat,yol,label_text)
		self.yol = yol
		box1.add(buton)
		box1.show_all()
		return box1	

	def geri(self,w,data=False):

		if self.editor().get_buffer().can_undo():
			self.editor().get_buffer().undo()		 
		else:		
			self.ileti.set_text( "Bellekte Başka Geri Alınıcak Argüman Yok..")

	def rgeri(self,w,data=False):
		if self.editor().get_buffer().can_redo():
			self.editor().get_buffer().redo()		 
		else:
			self.ileti.set_text( "Bellekte Başka Tekrar Yapılıcak Argüman Yok..")

	def mesaj(self,msj):
		dialog = gtk.MessageDialog(type=gtk.MessageType.INFO, buttons=gtk.ButtonsType.OK)
		dialog.set_markup(msj)
		dialog.show()
					
		if dialog.run() == gtk.ResponseType.OK:
			dialog.destroy()   

	def hata(self,msj):
		buffer = self.editor().get_buffer()
		pixbuf =  GdkPixbuf.Pixbuf.new_from_file_at_size("gtk-cancel.png",128,128)
		iter = buffer.get_iter_at_offset(0)
		buffer.insert(iter,"\n\n")
		buffer.insert_pixbuf(iter, pixbuf)
		buffer.insert(iter,msj)
		tag = buffer.create_tag( foreground="black",
					paragraph_background="#7F3731",
					right_margin=0,
					indent=50,
					left_margin=0,
					size_points=15.0,
					wrap_mode=gtk.WrapMode.WORD )
		s, e = buffer.get_bounds()
		buffer.apply_tag(tag, s,e )
		self.editor().set_editable(False)
		self.editor().set_border_window_size(gtk.TextWindowType.LEFT, 0)
		buffer.set_modified(False)

	def sablon(self,dosya,connect):
		builder = gtk.Builder()        
		builder.add_from_file(dosya)	
		vbox = builder.get_object("vbox1")
		self.pencere = builder.get_object("window1")
		self.pencere.set_modal(True)  
		ekle = gtk.Button(" Tamam ")
		ekle.connect("clicked", connect)
		vbox.add(ekle)    	
		self.pencere.show_all()	 
		return builder
	
	def sudo(self, su):
		build = self.sablon("../Glade/sudo.glade", self.SUDO) 
		self.su = {}
		for en, label in zip(range(1,5), range(5,9)):
			self.su[en] =  build.get_object("entry"+str(en))
			self.su[label] = build.get_object("label"+str(en))

	
	def yazilim(self, yazi):
		build = self.sablon("../Glade/yazılım.glade" , self.yaz)

		self.grs = {}
		for en, lb in zip(range(1,9), range(9,18) ):
			self.grs[en] =  build.get_object("entry"+str(en)) 
			self.grs[lb] =  build.get_object("label"+str(en)) 

	
	
	def eklenti(self, firefox):
		build = self.sablon("../Glade/firefox.glade" , self.ekle)

		self.giris = {}
		for en, lb in zip( range(1,6), range(6,12) ):
			self.giris[en] =  build.get_object("entry"+str(en)) 
			self.giris[lb] =  build.get_object("label"+str(en)) 

		 
	def kategori(self,kategori):		
		self.pencere = gtk.Window()
		self.pencere.set_size_request(400,-1)
		self.pencere.set_modal(True)  
		self.pencere.set_resizable(False)	
		self.pencere.set_title("Yazınız İçin Kategori")
		self.pencere.set_icon_from_file("../Simgeler/Z-kategori.png")
		box = gtk.VBox()

		self.bilgi = {}

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
			self.bilgi[order] = bilg

		hbox = gtk.VBox()

		self.radio = {}
		for buton, order in zip(self.bilgi,range(1, len(self.bilgi)+1)):
			if order == 1:
				self.radio[order] =  gtk.RadioButton(None,None)
			else:	
				self.radio[order] =  gtk.RadioButton.new_from_widget(self.radio[order-1])
			
			hbox.add(self.radio[order])


		dume = gtk.Button("Tamam")
		dume.connect("clicked", self.den)

		kutu = gtk.Table(4,4)
		kutu.set_border_width(12)
		kutu.set_col_spacings(8)	
		kutu.set_row_spacings(10)
		kutu.attach(hbox,0,1,1,2)
		kutu.attach(box,1,2,1,2)
		kutu.attach(dume,0,4,3,4)
		self.pencere.add(kutu)
		self.pencere.show_all()
	
	def arama(self, w, data=False):
		wiki = self.notebook.get_nth_page(self.tab_N)
		wiki.arama(w,False)

	def tercihler(self,w,data=False):
     
		def ayar(w,data=False): self.pencere.destroy(); self.ayar()

		self.notebook.show()	
		if self.notebook.get_n_pages() < 1:
			self.sek(1,False,False)
			self.editor().get_buffer().set_text(ar.lisans)
			self.editor().get_buffer().insert_at_cursor(ar.ksayol)

			self.editor().get_buffer().set_modified(False)
   
		builder = gtk.Builder()        
		builder.add_from_file("../Glade/tercihler.glade")	
		vbox = builder.get_object("hbuttonbox1")
		self.pencere = builder.get_object("window1")
	#	self.pencere.set_modal(True)  
		self.pencere.connect("delete_event",ayar)


		data = self.ayar(True)

		kapat = gtk.Button("Kapat")
		yar = gtk.Button("Yardım")
		yar.connect("clicked",self.pes)
		vbox.add(yar)
		vbox.add(kapat)
		kapat.connect("clicked",ayar)
		
		self.aadj =  builder.get_object("spinbutton1")	
		self.aadj.connect("value_changed",self.adj)

		self.aadj.set_value(float(data["sekme"][0] ) )


		self.yazi = builder.get_object("fontbutton1")
		self.yazi.set_font_name(data["font"][0])

		self.but =  builder.get_object("checkbutton1")	
		self.but.connect("toggled",self.sayi)

		self.but.set_active(eval(data["sekmeleri_say"][0] ))


		self.buton =  builder.get_object("checkbutton2")
		self.buton.connect("toggled",self.yazil)

		self.buton.set_active(eval(data["yazi_tipi"][0] ))

		self.wrap_mode = {1:["WORD"], 2:["CHAR"], 3:["NONE"]}

		for add in range(1,4):

			self.wrap_mode[add].extend( [builder.get_object("radiobutton"+str(add)), False] )
			self.wrap_mode[add][1].connect("clicked",self.radio_wrap)

			if self.wrap_mode[add][0] == data["wrap_mode"][0]:
				self.wrap_mode[add][1].set_active(True)


		self.pencere.show_all()

	def pes(self,pes):
		self.mesaj("Biri Buna Basar Demiştim Zaten...\n"+\
      				"""Yardım Almak İçin <a href= "http://www.ubuntu-tr.net\" >Ubuntu Türkiye</a> """)	

	def adj (self,oro):	
		a = str(self.aadj.get_value())
		b = a.strip("0.")
		self.editor().set_tab_width(int(b))	
						   
	def yazil(self,data):
		if self.buton.get_active() == True:
			self.editor().modify_font(None)
		else:    		
			self.yazitipi =  self.yazi.get_font_desc()
			self.editor().modify_font(self.yazitipi)

	def sayi(self,data):
		if self.but.get_active() == True:
			self.editor().set_border_window_size(gtk.TextWindowType.LEFT,  57)
			self.editor().set_show_line_numbers(True)
		else:    		
			self.editor().set_border_window_size(gtk.TextWindowType.LEFT,  0)

	def radio_wrap(self,ef=False):	

		for radio in self.wrap_mode:

			self.wrap_mode[radio][2] = self.wrap_mode[radio][1].get_active()

			if self.wrap_mode[radio][1].get_active():
				if ef is True:
					return self.wrap_mode[radio][0]
				self.editor().set_wrap_mode(getattr(gtk.WrapMode, self.wrap_mode[radio][0]))
				break
		#	print(self.wrap_mode[radio])
   		
	def ac(self, w, data=False):
		dialog = gtk.FileChooserDialog("Okumak ve değiştirmek için bir doysa seç..",
												None,
												gtk.FileChooserAction.OPEN,
												(gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
												gtk.STOCK_OPEN, gtk.ResponseType.OK))	
		dialog.set_default_response(gtk.ResponseType.OK)
		dialog.set_icon_from_file("wiki-editor.png")
		filter = gtk.FileFilter()
		filter.set_name("Tüm Dosyalar")
		filter.add_pattern("*")
		txt = gtk.FileFilter()
		txt.set_name("txt")
		txt.add_pattern("*txt")
		dialog.add_filter(filter)
		dialog.add_filter(txt)
		response = dialog.run()   	
	
		if response == gtk.ResponseType.OK:
			bilgi = dialog.get_filename()
			self.sek(1,bilgi,bilgi)
			self.open(bilgi)
			dialog.destroy()	 
	
		else:
			dialog.destroy()	 

	def ayar(self,data=False):	

		if not os.path.isfile(wiki_db):
			os.system("cp wiki_editor.db "+wiki_db)

		con = sqlite3.connect(wiki_db)
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

		wrap_mode = self.radio_wrap(True)
		
		data = {
			"sekme": [ str(self.aadj.get_value()),"set_tab_width"],
			"font": [str(self.yazi.get_font_name()),"modify_font"],
			"yazi_tipi": [str(self.buton.get_active()),"modify_font"],
			"sekmeleri_say": [ str(self.but.get_active()), "set_show_line_numbers"],
			"wrap_mode":[wrap_mode, "set_wrap_mode"],
			}
		

	#	con.commit()			
	#	cur.execute("CREATE TABLE settings(preference, value)")
	#	cur.executemany("INSERT INTO settings VALUES(?, ?) ", data)
	
	#	cur.executemany("REPLACE INTO settings VALUES(?, ?) ", data)
	#	con.commit()			
	#	con.execute("SELECT preference, value, COUNT(*) FROM settings GROUP BY  preference, value HAVING COUNT(*)>1")
	#	cur.execute("SELECT * FROM settings")
	#	con.execute("""DELETE FROM settings
	#	WHERE  preference NOT IN (
	#		SELECT MIN( preference)
	#		FROM settings
	#		GROUP BY preference, value
	#	); """)
	#q	con.commit()			
		for i in data:
			preference = i
			value = data[i]
			# print(preference, value)
			cur.execute("UPDATE  settings SET value='"+ value[0] +"|" + value[1] +"' WHERE preference='%s'" % preference) 

		con.commit()	
		#print('Results:', results)
		# store all the fetched data in the ans variable
		self.ayarlar()

	def ayarlar(self):

		data = self.ayar(True)

		for settings in sorted(data):
			set_value_as = data[settings][0]
			set_value = data[settings][1]

			if  settings == "wrap_mode":
				self.editor().set_wrap_mode(getattr(gtk.WrapMode, set_value_as))

			elif settings == "font":
				self.yazitipi = pango.FontDescription(set_value_as)
				self.editor().modify_font(self.yazitipi)

			elif settings == "yazi_tipi" and eval(set_value_as) is True:
				undo_font = getattr(self.editor(), set_value)(None)

			elif "sekme" == settings:
				getattr(self.editor(), set_value) (int(set_value_as.split(".0")[0]))

			elif "sekmeleri_say" == settings:
				getattr(self.editor(), set_value) (eval(set_value_as))


	def tasi(self, w, data=False):
		self.dialog = gtk.FileChooserDialog("Değişikliklerle Birlikte Metni Kaydet..",
												None,
												gtk.FileChooserAction.SAVE,
												(gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
												gtk.STOCK_SAVE, gtk.ResponseType.OK))	
		
		self.dialog.set_default_response(gtk.ResponseType.OK)
		self.dialog.set_icon_from_file("wiki-editor.png")
		self.dialog.set_current_name(self.yol)
		filter = gtk.FileFilter()
		filter.set_name("Tüm Dosyalar")
		filter.add_pattern("*")
		txt = gtk.FileFilter()
		txt.set_name("txt")
		txt.add_pattern("*txt")
		self.dialog.add_filter(filter)
		self.dialog.add_filter(txt)
		
		response = self.dialog.run()   	
		
		if response == gtk.ResponseType.OK:
			bilgi = self.dialog.get_filename()
			start, end = self.editor().get_buffer().get_bounds()
			konu= self.editor().get_buffer().get_slice(start, end, w)
			
			try:
				dosya = open(bilgi ,"w")
			except IOError as mesaj:
				hata = bilgi +"\nDosyası Kayıt Edilemedi..\nHata Kodu:-1\nHata Mesajı:"+str(mesaj)
				self.mesaj(hata)
				self.dialog.destroy()	
			else:	
				dosya.write(konu)
				dosya.close()
				self.dialog.destroy()	  
				page = self.notebook.get_current_page()
				self.notebook.remove_page(page)	

				self.sek(1,bilgi,bilgi)
				self.open(bilgi)
		else:
			self.dialog.destroy()	

	def secim(self, par, ca ):
		if  self.editor():
			buffer = self.editor().get_buffer()
			bounds = buffer.get_selection_bounds()
			self.konu = None
			if bounds:
				start, end = bounds
				self.konu = self.editor().get_buffer().get_slice(start, end,1)

				self.editor().get_buffer().begin_user_action()
				self.editor().get_buffer().delete(start, end)
				self.editor().get_buffer().insert_at_cursor(par + self.konu + ca)
				self.editor().get_buffer().end_user_action()
				return True
			else:
				self.ileti.set_text("Seçili hiç bir metin yok !")
				return None 		
		else:
			return None	

	
	def SUDO(self, SUDO):

		for x, y in zip(range(1,5), range(5,9)):
			if not self.su[x].get_text():
				self.mesaj(self.su[y].get_text() + "\nOlduğunu belirtin!")
				return False

		self.editor().get_buffer().begin_user_action()
		self.editor().get_buffer().insert_at_cursor("{{dergi|sayı=" + self.su[1].get_text() +\
											"|tarih="  + self.su[2].get_text() +  "|sayfano=" + \
											self.su[3].get_text() +"|yazar=" + self.su[4].get_text() + "}}")
		self.editor().get_buffer().end_user_action()

		self.pencere.destroy()
	
	def yaz(self, ya):
		
		for en, lb in zip(range(1,9), range(9,18) ):
			if not self.grs[en].get_text(): 
				self.mesaj(self.grs[lb].get_text()+"\nBoş bırakılmamalı!")
				return False

		self.editor().get_buffer().begin_user_action()
		self.editor().get_buffer().insert_at_cursor("{{yazılım|isim=" + self.grs[1].get_text() + "|ekran_görüntüsü=" +\
								self.grs[2].get_text() + "|açıklama=" + self.grs[3].get_text() + "|geliştirici=" + self.grs[4].get_text() +\
								"|depo=" + self.grs[7].get_text() + "|tür=" + self.grs[5].get_text() + "|lisans=" + \
								self.grs[6].get_text() +" |web_sitesi=" + self.grs[8].get_text() + "}}")
		self.editor().get_buffer().end_user_action()
		self.pencere.destroy()
   
	def  ekle(self, ek):
	
		for en, lb in zip(range(1,6), range(6,12)):
			if not self.giris[en].get_text():
				self.mesaj(self.giris[lb].get_text() +"\nBoş Bırakılmamalı!")
				return False	

		self.editor().get_buffer().begin_user_action()

		self.editor().get_buffer().insert_at_cursor("{{firefoxeklentisi|isim=" +self.giris[1].get_text() +\
					"|ekran_görüntüsü=" + self.giris[2].get_text() + "|açıklama=" + self.giris[3].get_text() +\
					"|geliştirici=" + self.giris[4].get_text() +"||web_sitesi=" + self.giris[5].get_text() + "}} ")
		
		self.editor().get_buffer().end_user_action()

		self.pencere.destroy()
	
	def anonim(self, sec):
		buffer = self.editor().get_buffer()
		bounds = buffer.get_selection_bounds()
		
		if bounds:
			start, end = bounds
			konu = self.editor().get_buffer().get_slice(start, end,1)
			renksec = gtk.ColorSelectionDialog("Bir renk seçin")
			renksec.set_icon_from_file("../Simgeler/07-renk seç.png")
			renksec.show()

			if renksec.run() == gtk.ResponseType.OK:
				self.editor().get_buffer().begin_user_action()
				self.editor().get_buffer().delete(start, end)
				renk = renksec.get_color_selection().get_current_color().to_floats()
				# crazy stuff here needs to change rgb01 to rgb250
				r, g, b = renk[0] * 255, renk[1] * 255,  renk[2] * 255
#				print(r,g,b)
				self.editor().get_buffer().insert_at_cursor('<span style="color:rgb(' + str(r)+", "+str(g)+", "+str(b)+');">' + konu + '</span>')
				self.editor().get_buffer().end_user_action()

				renksec.destroy()
    
			else: renksec.destroy()

		else: self.ileti.set_text("Seçili hiç bir metin yok !")
	
	def den(self, deneme):

		for number in self.radio:
			if self.radio[number].get_active():
				iter = self.bilgi[number].get_active_iter()
				model = self.bilgi[number].get_model()
				konu = model[iter][0] 
				self.editor().get_buffer().insert_at_cursor("[[kategori:" + konu +"]]")
 

		self.pencere.destroy()

	def sed(self,komut):		
		buffer = self.editor().get_buffer()
		bounds = buffer.get_selection_bounds()
  
		if bounds:
			start, end = bounds
			konu = self.editor().get_buffer().get_slice(start, end,None)
			self.editor().get_buffer().begin_user_action()

			self.editor().get_buffer().delete(start, end)
			dosya = open("/tmp/wiki-editor","w")
			dosya.write(konu)
			dosya.close()
			os.system(komut)
	
			dosya = open("/tmp/wiki-editor","r")
			self.editor().get_buffer().insert_at_cursor(dosya.read())
			
			self.editor().get_buffer().end_user_action()

			dosya.close()
			os.system("rm -rf /tmp/wiki*")  	
			return True
		else:
			self.mesaj("Seçili Hiç Bir Metin Yok!")			
			return None

	def nooo(self, w, data=False):
		if  w.get_label() ==  "Wiki Kodlarını Pasifleştir": self.sed(ar.no)		
		elif w.get_label() ==  "Wiki Kodlarını Pasifleştirme": self.sed(ar.rno)	     
  	
	def madde(self, w, data=False):	

		if w.get_label() == "Maddele": self.sed(ar.madde)
		elif  w.get_label() == "Maddeleme": self.sed(ar.rmadde)
	
	def bosluk(self, w, data=False):
		if  w.get_label() ==  "Boşlukları Kodla": self.sed(ar.bosluk)
		elif w.get_label() ==  "Boşlukları Kodlama": self.sed(ar.rbosluk)

	def set_tool(self,w,data=False):
		if w.get_label() ==  "Sadece Simge": self.toolbar.set_style(gtk.ToolbarStyle.ICONS)
		elif w.get_label() ==  "Sadece Metin": self.toolbar.set_style(gtk.ToolbarStyle.TEXT)
		else: self.toolbar.set_style(gtk.ToolbarStyle.BOTH)
  
#		neye =  str(self.toolbar.get_style()).strip("><")
#		for i in "_":
#			neye=neye.replace(i, "")
#		self.conf("/apps/wiki-editor/toolbar",  str(neye))	
			
	def tam(self, w, data=False):

		if self.full_screen == None: self.pen.fullscreen() ; self.full_screen = True
		else: self.pen.unfullscreen() ; self.full_screen = None

	def yeni(self,w=False): self.sek(False,False,0)	
	def kurulum(self,  w, data=False): os.system('xdg-open http://wiki.ubuntu-tr.net/index.php/Acemiler_i%C3%A7in_Wiki&')
	def katil(self,  w, data=False): ol.Uyeol().main()

	def soru(self,  w, data=False):
		i = -1
		while True:
			i += 1
			self.notebook.set_current_page(i)
			page = self.notebook.get_current_page()
			if  self.notebook.get_n_pages() < i:
				exit()
			elif self.editor():
				if self.editor().get_buffer().get_modified():
					soru = gtk.MessageDialog(type=gtk.MessageType.QUESTION , buttons=gtk.ButtonsType.YES_NO)
					soru.set_markup("<b>Kayıt Edilmemiş Değişiklikler Var </b>\n<i>Yine de Programdan çıkmak istediğinize emin misiniz?</i>")
					if soru.run() == gtk.ResponseType.YES:
						soru.destroy()	
						exit()
					else:
						soru.destroy()
						gtk.main()
				elif self.notebook.get_n_pages() == 1:			
						exit()
				else:
					pass					
			else:
				exit()

	def deger(self, w,data=False):
	#	print(w.get_label())
		if w.get_label() ==  "Sola Hizala": self.editor().set_left_margin(20)
		elif  w.get_label() == "Ortala": self.editor().set_left_margin(400)
		elif  w.get_label() == "Sağa Hizala": self.editor().set_left_margin(800)

	def kayit(self,w,data=False):

		if  "Kaydedilmemiş" in self.yol: self.tasi(1,1)
		else:
			start, end = self.editor().get_buffer().get_bounds()
			konu= self.editor().get_buffer().get_slice(start, end,w)
			try:
		#		print(self.yol)
				dosya = open( self.yol ,"w")
			except IOError as mesaj:
				hata = self.yol+ "\nDosyası Kayıt Edilemedi..\nHata Kodu:-2\nHata Mesajı:"+str(mesaj)
				self.mesaj(hata)
			dosya.write(konu)
			dosya.close()	
			self.ileti.set_text("' "+ self.yol + "' dosyası kayıt edildi..")
	#		self.editor().get_buffer().set_modified(False)

	def yazdir(self,w,data=False):
		page = self.notebook.get_current_page()
		wiki = self.notebook.get_nth_page(page)
	#	print("it works")
		wiki.yazdir(w,data=self.yol)

	def open(self,dosya):
 
		try:
			das = open(dosya,"r")
		except IOError as mesaj:
			hata =  str(dosya) + "\n\tDosyası Açılamadı\n\tHata Kodu:-3\n\tHata Mesajı:" +str(mesaj) +"\n\n\n"
			self.hata(hata)
			return False
		try:	
			u = das.read()
			self.editor().get_buffer().set_text(u)
		except Exception: 
			self.hata(" Hata Kodu:5 \n\tHata Mesajı:"+ str(dosya) + "\n\tdosyası okunurken hata oluştu!\n\n\n ")
			return False
	#		self.editor().get_buffer().set_data('languages-manager', lm)
	#		manager = self.editor().get_buffer().get_data('languages-manager')
 
		language = self.lm.guess_language(dosya)
		self.editor().get_buffer().set_language(language) 
		self.editor().get_buffer().set_undo_manager()
		self.editor().get_buffer().set_modified(False)

		self.label.set_text("language")
		das.close()
