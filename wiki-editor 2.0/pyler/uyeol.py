#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#import mechanize , cookielib, some coool stuff here
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
import sys,os
import araclar as ar
class Uyeol(gtk.Assistant):
	def __init__(self):
		gtk.Assistant.__init__(self)
		self.connect('close', self.kapat)
		self.connect('cancel', self.kapat)
		self.set_title("Üye Ol - Wiki Editor")
		self.set_icon_from_file("üye.png")
		self.set_resizable(False)
		#self.set_position(gtk.WIN_POS_CENTER)
		self.set_modal(True)
		#self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)  
		self.uy = str()
		#Sayfa 1
		table = gtk.Table(2,2)
		table.set_row_spacings(15)	
		table.set_border_width(5)
		resim = gtk.Image()
		resim.set_from_file("wikiubuntu-tr.png")
		bilgi = gtk.Label()
		bilgi.set_markup(ar.tayfa)
		frame = gtk.Frame()
		frame.add(bilgi)
		table.attach(resim,0,1,0,1)
		table.attach(frame,0,1,1,2)
		table.show_all()
		self.append_page(table)
		self.set_page_title(table, 'Wiki Ve Wiki Tayfası Hakkında ')
		self.set_page_type(table, gtk.AssistantPageType.CONTENT)
		self.set_page_complete(table,True)		
		#Sayfa 2
		global kullaniciadiraw, sifreraw ,email , isim
		kullaniciadiraw = gtk.Entry()
		sifreraw =  gtk.Entry()
		email =  gtk.Entry()
		isim =  gtk.Entry()
		sifreraw.set_visibility(False)
		h = gtk.Label()
		h.set_markup('<span foreground="#550085"  size="x-large" font_family="URW Chancery L "><b>Kullanıcı Adınız  ? </b></span>')
		hh = gtk.Label()
		hh.set_markup('<span foreground="#550085"  size="x-large" font_family="URW Chancery L "><b>Şifreniz  ?</b></span>')
		hhh = gtk.Label()
		hhh.set_markup('<span foreground="#550085"  size="x-large" font_family="URW Chancery L "><b>Email Adresiniz  ?</b></span>')
		hhhh = gtk.Label()
		hhhh.set_markup('<span foreground="#550085"  size="x-large" font_family="URW Chancery L "><b>Gerçek İsminiz   ?</b></span>')
		tamam = gtk.Button("Tamam")
		tamam.connect("clicked",self.hehe)
		table = gtk.Table(9,5)
		table.set_col_spacings(10)
		table.set_row_spacings(25)  
		table.set_border_width(65)
		table.attach(h,0,1,0,1)
		table.attach(kullaniciadiraw,1,2,0,1)
		table.attach(hh,0,1,1,2)
		table.attach(sifreraw,1,2,1,2)
		table.attach(hhh,0,1,2,3)
		table.attach(email,1,2,2,3)
		table.attach(hhhh,0,1,3,4)
		table.attach(isim,1,2,3,4)
		table.attach(tamam,0,4,8,9)
		table.show_all()
		self.append_page(table)		
		self.set_page_title(table, 'Gerekli Kullanıcı Bilgileri')
		self.set_page_type(table, gtk.AssistantPageType.CONTENT)		
		#Sayfa 3
		vbox = gtk.VBox()
		label = gtk.Label()
		label.set_markup('<span foreground="#550085"  size="xx-large" font_family="URW Chancery L "><b>"Üye Olma İşlemi Başarıyla Gerçekleşti!"</b></span>')
		global butn
		resim = gtk.Image()
		resim.set_from_file("üye.png")
		butn = gtk.CheckButton("Onaylama Mesajı İçin Mail'e Git")
		vbox.add(resim)
		vbox.set_border_width(80)
		vbox.add(label)
		vbox.add(butn)
		vbox.show_all()
		self.append_page(vbox)		
		self.set_page_title(vbox,"İşlem Tamamlandı!" )
		self.set_page_type(vbox, gtk.AssistantPageType.SUMMARY)
	def mesaj(self,msj):
		dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=True)
		dialog.set_markup(msj)
		if dialog.run() == gtk.RESPONSE_OK:
			dialog.destroy()
	def hehe(self,table):
		if not kullaniciadiraw.get_text():
			self.mesaj("Kullanıcı adı boş bırakılmamalı!") 
		elif  len(sifreraw.get_text())  < 4 :
			self.mesaj("Güvenliğiniz için şifre en az 4 haneli olmalıdır.")
		elif not email.get_text():
			self.mesaj("Email adresi gereklidir!")
		else:	
			self.uy = "Yeni Üye " + kullaniciadiraw.get_text()
			br = mechanize.Browser()
			cj = cookielib.LWPCookieJar()
			br.set_cookiejar(cj)
			br.set_handle_equiv(True)
			br.set_handle_gzip(True)
			br.set_handle_redirect(True)
			br.set_handle_referer(True)
			br.set_handle_robots(False)
			br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
			br.open("http://wiki.ubuntu-tr.net/index.php?title=%C3%96zel:Kullan%C4%B1c%C4%B1Giri%C5%9F&type=signup")
			br.select_form(nr=0) 
			br["wpName"]=kullaniciadiraw.get_text()
			br["wpPassword"]=sifreraw.get_text()
			br["wpRetype"]=sifreraw.get_text()
			br["wpEmail"]=email.get_text()
			br["wpRealName"]=isim.get_text()
			br.submit()
			self.set_page_complete(table.get_parent(),True)	  
	def kapat(self, assistant):
		if butn.get_active():
			os.system("gnome-open " + email.get_text() + "& ")
			self.destroy()
		else:
			self.destroy()
	def main(self):
		self.show()