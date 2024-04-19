# -*- coding: utf-8 -*-     
import gi
gi.require_version('GtkSource', '4')
from gi.repository import GObject as gobject
from gi.repository import GtkSource as edit
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk 
from gi.repository import GdkPixbuf
from gi.repository import Pango as pango

import os, re
import sqlite3
import araclar as ar
import wikitext as wiki
import uyeol as ol

from araclar import menu_setup
from araclar import get_stock
from araclar import get_filechooser
from araclar import mesaj
from araclar import hata


TARGET_TYPE_URI_LIST = 80
wiki_db = os.environ['HOME']+"/.wiki_editor.db"
UI_INFO = ar.UI_INFO
SIMGELER = ar.simgeler
FULL_SCREEN = None
VISIT_PAGE = 'http://wiki.ubuntu-tr.net/index.php/Acemiler_i%C3%A7in_Wiki&'

TMP_FILE = ar.TMP_FILE


UNDEFINED_LIST = {}

class hitokiri(object):

	def __init__(self):
		
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
			( "Yeni",  None,"Yeni",   "<control>N", None, lambda x: self.yeni(False)),
			( "Aç",    None,"Aç",  "<control>O", None, self.ac ),     
			( "Kaydet",  None, "Kaydet","<control>S", None, self.kayit),
			( "Farklı Kaydet",  None, "Farklı Kaydet","<shift><control>S", None, self.save_as ),
			( "Yazdır", None, "Yazdır", "<control>Y", None, self.yazdir),     
			( "Çık", None, "Çık", "<control>Q", None, self.soru),
			( "Düzen", gtk.Action(name="Düzen"), "Düzen"),
			( "Geri Al", None,"Geri Al",  "<control>Z", None, self.geri ),          
			( "Tekrar Yap", None,"Tekrar Yap", "<shift><control>Z", None, self.tekrar_yap),
			( "Hizalama", None,"Hizalama" ),   
			( "Sola Hizala",None,"Sola Hizala",None, None, self.set_tool_edit),
			( "Ortala",None ,"Ortala",None, None, self.set_tool_edit),                  
			( "Sağa Hizala",None ,"Sağa Hizala",None, None, self.set_tool_edit),      
			( "Tercihler", None, "Tercihler",  "<control>P", None, self.tercihler),      
			( "Bul", None, "Bul", "<control>F",None, self.arama),     
			( "Görünüm", gtk.Action(name="Görünüm"), "Görünüm" ),
			( "Sadece Simge",   None,"Sadece Simge",  None, None, self.set_tool_edit),
			( "Sadece Metin",  None, "Sadece Metin", None, None, self.set_tool_edit),
			( "Metin ve Simge", None,"Metin ve Simge", None, None, self.set_tool_edit),             
			( "Tam Ekran",  None, "Tam Ekran", "F11", None, self.change_screen ),     
			( "Araçlar",gtk.Action(name="Araçlar"), "Araçlar"),            
			( "Boşlukları Kodla", None,"Boşlukları Kodla", "<control>E",None, self.sed_setup ),
			( "Boşlukları Kodlama", None, "Boşlukları Kodlama", "<control><shift>E", None, self.sed_setup),
			( "Wiki Kodlarını Pasifleştir", None,"Wiki Kodlarını Pasifleştir",  "<control>W",None, self.sed_setup ),	    
			( "Wiki Kodlarını Pasifleştirme",None, "Wiki Kodlarını Pasifleştirme","<control><shift>W",None, self.sed_setup ),
			( "Maddele", None, "Maddele",  "<control><shift>M", None, self.sed_setup ),
			( "Maddeleme", None, "Maddeleme", "<control><shift>N", None, self.sed_setup ),	   			
			( "Yardım", gtk.Action(name="Yardım"),"Yardım" ),
			( "İçindekiler", None, "İçindekiler" , "F1", None, lambda x: os.system('xdg-open %s' %(VISIT_PAGE))),
			( "Bize Katılın", None, "Bize Katılın", "F2", None, lambda x:  ol.Uyeol().main() ),	    
			( "Hakkında", None ,"Hakkında",None, None, ar.hakkinda),
			]

		box = gtk.VBox(False, 0)
		box.show()
		
		self.menubar = self.get_main_menu(pencere)
		box.pack_start(self.menubar, False, True, 0)
		self.menubar.show()

################ variable can be passed too.####################################
#		wiki.ileti = self.ileti
#		wiki.statu = self.statu
####################################################
		self.statu = gtk.Statusbar()
		self.statu.set_size_request(150,10)
		self.ileti = gtk.Label()
############
		self.hbox = gtk.HBox()
		buton =  self.menu(ar.langs) 
		self.toolbar = self.toolmake()		

		self.hbox.pack_start(self.ileti,True,False,0)
		self.hbox.pack_end(buton,False,True,30)
		self.hbox.pack_start(self.statu,False,True,0)

		self.hide  = gtk.Toolbar()
##################################################33		
		self.tool_active = self.hide
	#	toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
	#	toolbar.set_style(gtk.TOOLBAR_BOTH)
		self.hide.set_border_width(4)

		uye = gtk.Image() 
		pix = GdkPixbuf.Pixbuf.new_from_file_at_size("üye.png",28,28)	
		uye.set_from_pixbuf(pix)	

		self.toolitem("Yeni","Yeni Bir Belge Oluştur", 
				get_stock( gtk.STOCK_FILE),
				lambda x: self.yeni(False)) 
		self.toolitem( "Aç",   "Bir Dosya Aç",
				get_stock(gtk.STOCK_OPEN),
				self.ac )     
		self.toolitem( "Tercihler",   "Wiki Editor Tercihleri ",
				get_stock( gtk.STOCK_PREFERENCES),
				self.tercihler )      
		self.toolitem( "Üye Ol",  
				"Henüz Wikiye Üye Değil Misin ?\nO Zaman Bu Tam Senin İçin ..",
				uye, lambda x:  ol.Uyeol().main()  )      
		
		self.toolitem( "Hakkında", 
				"Wiki Editor Hakkında",
				ar.hak,ar.hakkinda )      

		table = gtk.Table(400,400)
		table.attach(self.notebook ,0,400,2,399)
		table.attach(self.toolbar,0,1,1,2)
		table.attach(self.hide,0,4,0,4)
		table.attach(box,0,1,0,1)
		table.attach(self.hbox,0,400,399,400)

		pencere.add(table)
		pencere.show_all()	
		self.hide.hide()
		self.pen = pencere 
		self.lm = edit.LanguageManager()
		self.showy_widgets_ = [ self.hbox, self.toolbar,self.menubar ]  

	def get_main_menu(self, pencere):

		uimanager = gtk.UIManager()
		action_group = gtk.ActionGroup(name="my_actions")
		action_group.add_actions(self.menu_items)

		uimanager.add_ui_from_string(UI_INFO)
		uimanager.insert_action_group(action_group)

		accelgroup = uimanager.get_accel_group()
		pencere.add_accel_group(accelgroup)

		return uimanager.get_widget("/MenuBar")

	def switch(self, tab=False, widget=False, tab_N=False):
	#	print(widget, tab_N)
		self.tab_N = tab_N
		hbox = tab.get_tab_label(widget)
		label = hbox.get_children()[1]
		self.name = label.get_text()
		text = label.get_tooltip_text()
		yol = text.split(":")[1]

		if os.path.isfile(yol):
			self.yol = yol
			return False
		
		self.yol = yol + text.split(":")[2]

	@property
	def current_editor(self):
		page = self.notebook.get_current_page()
		sw = self.notebook.get_nth_page(page)
		try:
			buffer = sw.get_widget()
			buffer.set_left_margin(8)

		except AttributeError:
			buffer = None
		return buffer
	
	@property
	def current_buffer(self):
		return self.current_editor.get_buffer()

	def menu(self,item):
		self.menu = gtk.Menu()
		for x in item:
			menu_items = gtk.MenuItem(x)   
			self.menu.append(menu_items)
			menu_items.connect("activate", self.menuitem_response, x)
			menu_items.show()

		ek = gtk.HBox()
		image = get_stock(gtk.STOCK_GO_DOWN)
		self.label = gtk.Label("Düz Metin")
		ek.pack_start(self.label,False,False,10)
		ek.pack_start(image,False,False,0)

		buton = gtk.Button()
		buton.set_relief(gtk.ReliefStyle.NONE)
		buton.connect_object("event", self.button_press, self.menu)
		buton.add(ek)
		buton.show()
		return buton

	def button_press(self, widget, event):
	#	print(widget, event.type)
		if event.type == gdk.EventType.BUTTON_PRESS:
	#		if event.button == 1:
			widget.popup(None, None, None, event.button, event.time, event.time)
			return True
		return False

	def menuitem_response(self, widget, string):
		self.label.set_text("%s" % string)
		self.change() 

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
		
		for item in SIMGELER:
			self.toolitem(item, SIMGELER[item][0], SIMGELER[item][1],SIMGELER[item][2])

		return toolbar  

	def toolitem(self, label, tooltip,resim,islem):
		item = gtk.ToolButton(resim, label)
		item.set_tooltip_text(tooltip)
		item.set_label(label)
		item.set_icon_widget(resim)

		if type(islem) is dict:
		# if islem is dict unpack dict and call self.sablon
			file_path, format_ = [ i for i in islem.items()][0]
			item.connect('clicked', lambda x: self.sablon(file_path, format_))
		elif type(islem) is list:
		# if islem is list send it to self.selection_
			item.connect('clicked',lambda x: self.selection_(islem[0], islem[1]) )
		# if it's a string call it as a fuction within hitokiri... 
		elif type(islem) is str:
			item.connect('clicked', getattr(self,islem))
		# if it's a fuction leave it as it is...
		else:
			item.connect('clicked',islem )
		
		item.show()
		self.tool_active.insert(item, -1) 

	def change(self,*args):
	#	self.current_editor().get_buffer().set_data('languages-manager', lm)
#		manager = self.current_editor().get_buffer().get_data('languages-manager')
		tip = self.label.get_text()
		lang = ar.langs[tip]
		language = self.lm.guess_language(content_type=lang)
		self.current_buffer.set_language(language) 	

	def yeni(self,yol, baslik="yok"):
		page_number = str( self.notebook.get_current_page() +2 )

		if not yol:
			baslik = "Kaydedilmemiş Belge: %s" %( page_number)
			yol = baslik
			# IF UNDEFINED NAME EXIST IN NOTEBOOK...
			if yol in [ UNDEFINED_LIST[n] for n in UNDEFINED_LIST]:
				#DEFINE NEW UNDEFINED AS +1 FROM THE CURRENT MAX NUMBER IN THE LIST
				page_number = max([ UNDEFINED_LIST[n] for n in UNDEFINED_LIST]).split(":")[1] 
				page_number = int(page_number)+1
				baslik = "Kaydedilmemiş Belge: %s" %( page_number)

			UNDEFINED_LIST[int(page_number)] = baslik

		else:	
			baslik = yol
			grep=re.findall(".*?../", baslik)
			for i in grep:
				baslik=baslik.replace(i, "")

		page_title = self.note_label_box( baslik,yol)
		wiki_text = wiki.wikieditor()		

		self.notebook.append_page( wiki_text, page_title)
		self.notebook.show_all()
		self.notebook.next_page()

		self.set_ayar(set_up=True)

	def kapat(self,widget,label_text):
     		
		i=-1
		
		while self.notebook.get_n_pages():
			
			i+=1
			self.notebook.set_current_page(i)
			
			get_n_widget = self.notebook.get_nth_page(i) # return wiki_editor
			get_n_tab_label = self.notebook.get_tab_label(get_n_widget) # return box
			get_n_info = get_n_tab_label.get_children()[1].get_text() # return box child list_ #image#label/button


			if label_text != get_n_info: continue

			global UNDEFINED_LIST
			# if get_n_info in UNDEFINED LIST
			if get_n_info in [ UNDEFINED_LIST[n] for n in UNDEFINED_LIST]:
			#	print(get_n_info)
			#	UNDEFINED_LIST.pop(i+1)
				#REMOVE get_n_info from UNDEFINED, REDUCE -1 each given index
				UNDEFINED_LIST = {key-1: val for key, val in UNDEFINED_LIST.items() if key != i+1 }
				# REDEFINE index info from 1 to N large from UNDEFINED INFO
				UNDEFINED_LIST = {key: UNDEFINED_LIST[val] for key, val in zip(range(1,len(UNDEFINED_LIST)+1),UNDEFINED_LIST ) }
			#	print(UNDEFINED_LIST)

			response_ = None 

			if self.current_buffer.get_modified():
				dialog = gtk.MessageDialog(type=gtk.MessageType.WARNING)
				dialog.add_button("Kaydetmeden Kapat",gtk.ResponseType.NO)
				dialog.add_button("İptal",gtk.ResponseType.CANCEL)
				dialog.add_button("Kaydet",gtk.ResponseType.OK)

				dialog.set_markup("<b>Kapatmadan önce <tt>'"+ label_text + \
					"'</tt> \nbelgesinde yaptığınız değişiklikleri kaydetmek ister misiniz?"+\
        			"</b>\n\n<i>Kaydetmediğiniz takdirde, yaptığınız son değişiklikler kaybolacak.</i>")
				
				dialog.show()
				response_ = dialog.run() 
				
				if response_ ==  gtk.ResponseType.OK: 
					self.kayit(self.name,1);dialog.destroy(); break

				elif response_ ==  gtk.ResponseType.CANCEL: dialog.destroy(); break

				self.notebook.remove_page(i); 
				

				dialog.destroy() 
				break
			else:
				self.notebook.remove_page(i)
				break



		if self.notebook.get_n_pages() == 0:
			self.hide.show(); 
			for hide in self.showy_widgets_: hide.hide() 			

	def note_label_box(self, label_text,yol):

		if self.notebook.get_n_pages()  == 0:
			self.hide.hide(); 
			for show in self.showy_widgets_: show.show() 

		box1 = gtk.HBox()
		image = get_stock(gtk.STOCK_CLOSE)
		image1 = get_stock(gtk.STOCK_FILE)	
		box1.add(image1)
		label = gtk.Label(label_text)
		box1.add(label)
		label.set_tooltip_text("Dosya yolu:" + str(yol))
		buton = gtk.Button()
		buton.add(image)
		buton.set_relief(gtk.ReliefStyle.NONE)
		buton.set_tooltip_text("Belgeyi Kapat" )	
		buton.set_size_request(24,24)
		buton.connect("clicked",self.kapat,label_text)
		self.yol = yol
		box1.add(buton)
		box1.show_all()
		return box1

	def geri(self,*args):

		if self.current_buffer.can_undo():
			self.current_buffer.undo()		 
		else:		
			self.ileti.set_text( "Bellekte Başka Geri Alınıcak Argüman Yok..")

	def tekrar_yap(self,*args):
		if self.current_buffer.can_redo():
			self.current_buffer.redo()		 
		else:
			self.ileti.set_text( "Bellekte Başka Tekrar Yapılıcak Argüman Yok..")

	def sablon(self,dosya,format_):
		builder = gtk.Builder()        
		builder.add_from_file(dosya)	
		vbox = builder.get_object("vbox1")
		self.pencere = builder.get_object("window1")
		self.pencere.set_modal(True)  
		
		dict_= {}
		range_ = len(format_.split("{}"))  # number of entries
		range_ = [ [1, range_], [range_, range_*2]]

		for en, lb in zip(range(*range_[0]), range(*range_[1]) ):
			dict_[en] =  builder.get_object("entry"+str(en)) 
			dict_[lb] =  builder.get_object("label"+str(en)) 

		ekle = gtk.Button(" Tamam ")
		ekle.connect("clicked", lambda x: self.set_en_label_text(dict_,range_,format_))
		vbox.add(ekle)

		self.pencere.show_all()	 

	def set_en_label_text(self, dict_,range_, format_):
		get_text = []
		for x, y in zip(range(*range_[0]), range(*range_[1]) ):
			if not dict_[x].get_text():
				mesaj(dict_[y].get_text() + "\nBoş bırakılmamalı!")
				return False
			get_text.append(dict_[x].get_text())

		self.set_text(format_.format(*get_text), True)
		self.pencere.destroy()

	def kategori(self,*args):
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
		for order in range(1, len(self.bilgi)+1):
			if order == 1:
				self.radio[order] =  gtk.RadioButton(None,None)
			else:	
				self.radio[order] =  gtk.RadioButton.new_from_widget(self.radio[order-1])
			
			hbox.add(self.radio[order])

		dume = gtk.Button("Tamam")
		dume.connect("clicked", self.radio_clicked)

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
     
		self.notebook.show()	
		if self.notebook.get_n_pages() < 1:
			self.yeni(False)
			self.current_buffer.set_text(ar.lisans+"\n"+ar.ksayol)
			self.current_buffer.set_undo_manager()
			self.current_buffer.set_modified(False)

   
		builder = gtk.Builder()        
		builder.add_from_file("../Glade/tercihler.glade")	
		vbox = builder.get_object("hbuttonbox1")
		self.pencere = builder.get_object("window1")

		self.pencere.connect("delete_event", 
				lambda *x: [x[0].destroy(),self.set_ayar() ]
			)
		
		data = self.set_ayar(True)

		kapat, yar = gtk.Button("Kapat"), gtk.Button("Yardım")

		yar.connect("clicked",
			lambda x: mesaj("Biri Buna Basar Demiştim Zaten...\n"+\
      		"""Yardım Almak İçin <a href= "http://www.ubuntu-tr.net\" >Ubuntu Türkiye</a> """)	
			)

		vbox.add(yar);vbox.add(kapat)

		kapat.connect("clicked", lambda *x:
				[self.pencere.destroy(), self.set_ayar() ]
			)
	
		self.font_spin =  builder.get_object("spinbutton1")	
		self.font_spin.connect( "value_changed", lambda *x:
					self.current_editor.set_tab_width(
					int( ("%s" % x[0].get_value()).strip("0.")) )
			)

		self.font_spin.set_value(float(data["sekme"][0] ) )


		self.yazi = builder.get_object("fontbutton1")
		self.yazi.set_font_name(data["font"][0])
		self.yazi.connect("font-set",
				lambda x: self.current_editor.modify_font(self.yazi.get_font_desc())
			)

		self.show_number =  builder.get_object("checkbutton1")	
		self.show_number.connect( "toggled",
				lambda x: self.current_editor.set_show_line_numbers(x.get_active() )
			)

		self.show_number.set_active(eval(data["sekmeleri_say"][0] ))


		self.modify_font =  builder.get_object("checkbutton2")
		self.modify_font.connect("toggled",self.yazil)

		self.modify_font.set_active(eval(data["yazi_tipi"][0] ))

		self.wrap_mode = {1:["WORD"], 2:["CHAR"], 3:["NONE"]}

		for add in range(1,4):

			self.wrap_mode[add].extend( [builder.get_object("radiobutton"+str(add)), False] )
			self.wrap_mode[add][1].connect("clicked",self.radio_wrap)

			if self.wrap_mode[add][0] == data["wrap_mode"][0]:
				self.wrap_mode[add][1].set_active(True)


		self.pencere.show_all()

	def yazil(self,*data):
		if self.modify_font.get_active() == True:
			self.current_editor.modify_font(None)
		else:    		
			self.yazitipi =  self.yazi.get_font_desc()
			self.current_editor.modify_font(self.yazitipi)

	def radio_wrap(self,selected_=False):

		for radio in self.wrap_mode:

			self.wrap_mode[radio][2] = self.wrap_mode[radio][1].get_active()

			if self.wrap_mode[radio][1].get_active():
				if selected_ is True:
					return self.wrap_mode[radio][0]
				self.current_editor.set_wrap_mode(getattr(gtk.WrapMode, self.wrap_mode[radio][0]))
				break
		#	print(self.wrap_mode[radio])

	def ac(self, *args):
		response, dialog = get_filechooser("Okumak ve değiştirmek için bir doysa seç..")
	
		if response == gtk.ResponseType.OK:
			bilgi = dialog.get_filename()
			self.yeni(bilgi); self.open(bilgi)

		dialog.destroy()	 

	def set_ayar(self,data=False,set_up=False):

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
###################################################################3
		# set_up data from wiki.db
		if set_up is not False:
			data = self.set_ayar(True)

			for settings in sorted(data):
				set_value_as, set_value = data[settings]
				
				if  settings == "wrap_mode":
					getattr(self.current_editor, set_value) (getattr(gtk.WrapMode, set_value_as))

				elif settings == "font":
					self.yazitipi = pango.FontDescription(set_value_as)
					getattr(self.current_editor, set_value)(self.yazitipi)

				elif settings == "yazi_tipi" and eval(set_value_as) is True:
					getattr(self.current_editor, set_value)(None)

				elif "sekme" == settings:
					getattr(self.current_editor, set_value) (int(set_value_as.split(".0")[0]))

				elif "sekmeleri_say" == settings:
					getattr(self.current_editor, set_value) (eval(set_value_as))
			return False
################################################################3
		###### update data from ui input ###############
		wrap_mode = self.radio_wrap(True)
		
		data = {
			"sekme": [ str(self.font_spin.get_value()),"set_tab_width"],
			"font": [str(self.yazi.get_font_name()),"modify_font"],
			"yazi_tipi": [str(self.modify_font.get_active()),"modify_font"],
			"sekmeleri_say": [ str(self.show_number.get_active()), "set_show_line_numbers"],
			"wrap_mode":[wrap_mode, "set_wrap_mode"],
			}
			
		for i in data:
			preference = i
			set_value, set_value_as = data[i]
			cur.execute("UPDATE  settings SET value='%s|%s' WHERE preference='%s'" \
						% (set_value,set_value_as,preference) )

		con.commit();self.set_ayar(set_up=True)

	def save_as(self, *args):
		response, dialog = get_filechooser("Değişikliklerle Birlikte Metni Kaydet..","SAVE")

		if response == gtk.ResponseType.OK:
			bilgi = dialog.get_filename()
			konu = self.get_konu(True)
			
			try:
				dosya = open(bilgi ,"w")
			except IOError as msj:
				hata = bilgi +"\nDosyası Kayıt Edilemedi..\nHata Kodu:-1\nHata Mesajı:"+str(msj)
				mesaj(hata)
			else:
				dosya.write(konu); dosya.close() 
				page = self.notebook.get_current_page()
				self.notebook.remove_page(page)	
				self.yeni(bilgi); self.open(bilgi)
		
		dialog.destroy()

	def set_text(self, text, insert=None):
			
		self.current_buffer.begin_user_action()
		if insert:
			self.current_buffer.insert_at_cursor(text)
		else:
			start, end = self.current_buffer.get_selection_bounds()
			self.current_buffer.delete(start, end)
			self.current_buffer.insert_at_cursor(text)
		self.current_buffer.end_user_action()

	def selection_(self, head_, tail_ ):

		konu = self.get_konu()

		if self.current_editor and konu:
			self.set_text(head_ + konu + tail_)
			return True
		else:
			self.ileti.set_text("Seçili hiç bir metin yok !")
			return None

	def get_konu(self, all_text=False):


		if all_text == True:
			start, end = self.current_buffer.get_bounds()
			konu= self.current_buffer.get_slice(start, end,1)
			return konu

		if bounds:=self.current_buffer.get_selection_bounds():
			start, end = bounds
			konu = self.current_buffer.get_slice(start, end,1)
			return konu
		else:
			self.ileti.set_text("Seçili hiç bir metin yok !")
			return False

	def color_select(self, sec):

		if konu:=self.get_konu():
			renksec = gtk.ColorSelectionDialog("Bir renk seçin")
			renksec.set_icon_from_file("../Simgeler/07-renk seç.png")
			renksec.show()

			if renksec.run() == gtk.ResponseType.OK:
				renk = renksec.get_color_selection().get_current_color().to_floats()
				# crazy stuff here needs to change rgb01 to rgb250
				self.set_text('<span style="color:rgb({}, {}, {} );">{}</span>'.\
				  format( *[i*255 for i in renk],konu))
			
			renksec.destroy()

	def radio_clicked(self, *arg):

		for number in self.radio:
			if self.radio[number].get_active():
				iter = self.bilgi[number].get_active_iter()
				model = self.bilgi[number].get_model()
				konu = model[iter][0] 
				self.set_text("[[kategori:" + konu +"]]",True)

		self.pencere.destroy()

	def sed_setup(self, widget, komut=None):

		for label in menu_setup["ARACLAR"]:
			if label == widget.get_label():
				komut = menu_setup["ARACLAR"][label]; break

		if konu:=self.get_konu():

			with open(TMP_FILE,"w") as dosya:
				dosya.write(konu)

			os.system(komut)

			with open(TMP_FILE,"r") as dosya:
				self.set_text(dosya.read())
	
			os.system("rm -rf %s" %(TMP_FILE) )

	def set_tool_edit(self,w,data=False):

		for label, label_ed in zip(menu_setup["GORUNUM"],menu_setup["HIZALAMA"]):

			if label in w.get_label():
				set_up = getattr(gtk.ToolbarStyle, "%s" %(menu_setup["GORUNUM"][label]) )
				self.toolbar.set_style(set_up); break

			elif label_ed in w.get_label():
				set_up = getattr(gtk.Justification, "%s" %(menu_setup["HIZALAMA"][label_ed]) )
				self.current_editor.set_justification(set_up); break

	def change_screen(self, *args):
		global FULL_SCREEN
		FULL_SCREEN = not FULL_SCREEN
		if 	FULL_SCREEN: self.pen.fullscreen()
		else: self.pen.unfullscreen()

	def soru(self,*args):
		i = -1
		while True:
			i += 1
			self.notebook.set_current_page(i)

			if  self.notebook.get_n_pages() < i: exit(0)

			elif self.current_editor:

				if self.current_buffer.get_modified():
					soru = gtk.MessageDialog(type=gtk.MessageType.QUESTION , buttons=gtk.ButtonsType.YES_NO)
					soru.set_markup("<b>Kayıt Edilmemiş Değişiklikler Var </b>"+\
					 "\n<i>Yine de Programdan çıkmak istediğinize emin misiniz?</i>")

					if soru.run() == gtk.ResponseType.YES: soru.destroy(); exit(1)

					else: soru.destroy(); gtk.main(); break

			else: exit(0)

	def kayit(self,*args):

		if  "Kaydedilmemiş" in self.yol: self.save_as()
		else:
			konu= self.get_konu(True)
			try:
		#		print(self.yol)
				dosya = open( self.yol ,"w")
			except IOError as msj:
				hata_ = self.yol+ "\nDosyası Kayıt Edilemedi..\nHata Kodu:-2\nHata Mesajı:"+str(msj)
				mesaj(hata_)
				return False 

			dosya.write(konu); dosya.close()	
			self.ileti.set_text("' "+ self.yol + "' dosyası kayıt edildi..")
			self.current_buffer.set_modified(False)

	def yazdir(self,w,data=False):
		page = self.notebook.get_current_page()
		wiki = self.notebook.get_nth_page(page)
	#	print("it works")
		wiki.yazdir(w,data=self.yol)

	def open(self,dosya):
 
		try:
			das = open(dosya,"r")
		except IOError as mesaj:
			hata_mesajı =  str(dosya) + "\n\tDosyası Açılamadı\n\tHata Kodu:-3\n\tHata Mesajı:" +str(mesaj) +"\n\n\n"
			hata(hata_mesajı)
			return False
		try:	
			u = das.read()
			self.set_text(u,True)
		except Exception: 
			hata(" Hata Kodu:5 \n\tHata Mesajı:"+ str(dosya) + "\n\tdosyası okunurken hata oluştu!\n\n\n ")
			return False
		
		das.close()

		language = self.lm.guess_language(dosya)
		try:
			lm = language.get_mime_types()[0]
			lm = re.sub(".*.-", "", lm)
			self.label.set_text(lm)

		except AttributeError:
			self.label.set_text("Düz Metin")

		self.current_buffer.set_language(language) 
		self.current_buffer.set_undo_manager()
		self.current_buffer.set_modified(False)
