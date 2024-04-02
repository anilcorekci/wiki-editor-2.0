#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#Yararlanılan Kaynaklar;
# http://www.pygtk.org/pygtk2tutorial/
#http://www.eurion.net/python-snippets/snippet/GtkSourceView%20Example.html


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GtkSource as edit

	
class wikieditor(gtk.ScrolledWindow):
	def __init__(self):
		gtk.ScrolledWindow.__init__(self)
	#	self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.add(self.widget())
	def widget(self):
		self.edit = edit.View()
		self.tbuffer =  edit.Buffer()
		self.edit.set_buffer(self.tbuffer)
		self.edit.set_wrap_mode(gtk.WrapMode.CHAR)	
	#	self.edit.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 57)
	#	self.edit.set_border_window_size(gtk.TEXT_WINDOW_RIGHT, 2)
		self.tbuffer.connect('changed' , self.update_cursor_position,self.edit)
		self.edit.set_size_request( 490, 70) 
		return self.edit
	def get_widget(self):
		return self.edit
	def arama(self, w, data):
		builder = gtk.Builder()        
		builder.add_from_file("../Glade/ara.glade")	
		self.search_text  = builder.get_object("entry1")
		self.search_text.set_size_request(170 ,30)
		self.search_text.connect("activate", self.devam)

		 #have look this again ....
		
		self.log =  builder.get_object("radiobutton1")
		self.log1 = builder.get_object("radiobutton2")
		self.log2  = builder.get_object("radiobutton3")

		buton = gtk.Button(" Bul ")
		buton.connect("clicked",self.devam) 
		box = builder.get_object("vbox1")
		box.add(buton)
		pencere = builder.get_object("window1")

	#	pencere.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)     	
		buffer = self.edit .get_buffer()
		bounds = buffer.get_selection_bounds()   	
		if bounds:
			start, end = bounds
			konu = self.edit .get_buffer().get_slice(start, end,w)
			self.search_text.set_text(konu)
		pencere.show_all()
		self.renk = self.edit .get_buffer().create_tag(background="yellow",foreground="#000000")   	

	def ara(self,  backward):
		buffer = self.edit .get_buffer()
		str = self.search_text.get_text()	
		start, end = buffer.get_bounds()
		buffer.remove_tag(self.renk, start, end)
		iter = buffer.get_iter_at_mark(buffer.get_insert())
		i = 0
		if backward:
			while True:
				bul = iter.backward_search(str, gtk.TextSearchFlags.TEXT_ONLY)
				if not bul:
					break
				match_start, match_end = bul
				i += 1
				buffer.apply_tag(self.renk, match_start, match_end)
				iter = match_start
		else:
			while True:
				bul = iter.forward_search(str, gtk.TextSearchFlags.TEXT_ONLY)
				if not bul:
					break
				match_start, match_end = bul
				i += 1
				buffer.apply_tag(self.renk, match_start, match_end)
				iter = match_end			
		if not str:
			ileti.set_text("Hiçbir Eşleşme Bulunamadı!")			
		elif i < 1:
			ileti.set_text("Hiçbir Eşleşme Bulunamadı!")
		else:
			ileti.set_text("%d Tane Eşleşme Bulundu.." % i)

	def  heim(self, hem):
		buffer = self.edit .get_buffer()
		iter = buffer.get_iter_at_mark(buffer.get_insert())
		str = self.search_text.get_text()	
		start, end = buffer.get_bounds()
		buffer.remove_tag(self.renk, start, end)	
		found = iter.backward_search(str,gtk.TextSearchFlags.TEXT_ONLY)
		if found:
			match_start, match_end = found
			buffer.apply_tag(self.renk,match_start,match_end)	
			buffer.select_range(match_start,match_end)
			iter = match_end
		else:
			ileti.set_text("Hiçbir Eşleşme Bulunamadı!")

	def devam(self,  forward):
		# this is where it should be changed...
		if self.log.get_active():
			self.ara(True)		
		elif self.log1.get_active():
			self.ara(False)	
		elif self.log2.get_active():
			self.heim(1)		


	def get_lines(self, first_y, last_y, buffer_coords, numbers):
		text_view = self.edit

        # Get iter at first y
		iter, top = text_view.get_line_at_y(first_y)

        # For each iter, get its location and add it to the arrays.
        # Stop when we pass last_y
		count = 0
		size = 0
		
		while not iter.is_end():
			y, height = text_view.get_line_yrange(iter)
			buffer_coords.append(y)
			line_num = iter.get_line() + 1
			numbers.append(line_num)
			count += 1
			if (y + height) >= last_y:
				break
			iter.forward_line()
		return count

	def update_cursor_position(self,buffer, view):

		tabwidth = view.get_tab_width()
		#pos_label = view.get_tab_pos()
		iter = self.tbuffer.get_iter_at_mark(self.tbuffer.get_insert())
		row = iter.get_line() + 1
		start = iter.copy()
		start.set_line_offset(0)
		col = 0
		while start.compare(iter) < 0:
			if start.get_char() == '\t':
				col += tabwidth - col % tabwidth
			else:
				col += 1
			start.forward_char()
		statu.push(False,('Sat: %d, Süt: %d' % ( row, col)))
		if  len(ileti.get_text()) >= 4:
			ileti.set_text("")


	def yazdir(self,w,data=False):	
	#	print ("it works!")
		window = self.edit.get_toplevel()
		buffer = self.edit.get_buffer()
			
		compositor = edit.PrintCompositor().new_from_view(self.edit )
		compositor.set_wrap_mode(gtk.WrapMode.CHAR)
		compositor.set_highlight_syntax(True)
		compositor.set_header_format(False, 'Yazılan Gün  %A', None, '%F')
		filename = data
		filename = str(filename)
		compositor.set_footer_format(True, '%T', filename, 'Sayfa %N/%Q')
		compositor.set_print_header(True)
		compositor.set_print_footer(True)
			
		print_op = gtk.PrintOperation()
		print_op.connect("begin-print", self.begin_print_cb, compositor)
		print_op.connect("draw-page", self.draw_page_cb, compositor)
		res = print_op.run(gtk.PrintOperationAction.PRINT_DIALOG, window)
			
		if res == gtk.PrintOperationResult.ERROR:
			self.hata("Hatalı Baskı Dosyası:\n\n" + filename)
		elif res == gtk.PrintOperationResult.APPLY:
			print  ('Baskı Dosyası: "%s"' % filename )

	def begin_print_cb(self,operation, context, compositor):
		while not compositor.paginate(context):
			pass
		n_pages = compositor.get_n_pages()
		operation.set_n_pages(n_pages)

	def draw_page_cb(self,operation, context, page_nr, compositor):
		compositor.draw_page(context, page_nr)