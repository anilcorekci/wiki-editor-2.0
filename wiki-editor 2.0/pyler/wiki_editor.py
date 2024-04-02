#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#Yararlanılan Kaynaklar;
# http://www.pygtk.org/pygtk2tutorial/
#http://www.eurion.net/python-snippets/snippet/GtkSourceView%20Example.html
#2010 Hitokiri > !
#Wiki Editor özgür bir yazılımdır, onu Özgür Yazılım
#Vakfı'nın yayınladığı GNU Genel Kamu Lisansı'nın 2.
#sürümü veya (tercihinize bağlı) daha sonraki sürümleri
#altında dağıtabilir ve/veya değiştirebilirsiniz.
##################################################################
##################################################################
#Wiki Editor  faydalı olacağı umut edilerek dağıtılmaktadır,
#fakat HİÇBİR GARANTİSİ YOKTUR; hatta ÜRÜN DEĞERİ
#ya da BİR AMACA UYGUNLUK gibi garantiler de
#vermez. Lütfen GNU Genel Kamu Lisansı'nı daha fazla
#ayrıntı için inceleyin.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk 
import sys
import notebook as pen
hito = pen.hitokiri()
	
if __name__ == "__main__":
	if len(sys.argv) < 2:
		hito.sek(1,False,False)	
	else:	
		dosya = sys.argv[1]
		hito.sek(1,dosya,dosya) 
		hito.open(dosya)		
	#hito.ayarlar()
	gtk.main()