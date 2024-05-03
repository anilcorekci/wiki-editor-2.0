# -*- coding: utf-8 -*-
#pylint: disable=E0611, E1101, C0415
"""
Return as a gtkScorlledWindow
contains gtkSourceView widget
"""
import os
import gi

from gi.repository import GtkSource as edit
from gi.repository import Gtk as gtk

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

ILETI = gtk.Label("From main function hito -> ileti gtk.label")
STATU = gtk.Menu #"From main function hito -> statu gtk.label"
radio_action = { 1:["ara",True], 2: ["ara",False], 3: ["back_ward",1] }

class WikiEditor(gtk.ScrolledWindow):
    """
    getting variables from __main__ hito
    """
    renk = None #foregroun color for search
    radio = None
    search_text = None

    def __init__(self):
        """
        initiliaze as a scrolled window
        """
        from __main__ import HITO as notebook
        globals()["ILETI"] = notebook.ileti
        globals()["STATU"] =  notebook.statu
        gtk.ScrolledWindow.__init__(self)
    #    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(self.widget())

    def get_widget(self):
        """
        return sourceView widget
        """
        return self.edit

    def widget(self):
        """
        main widge
        """
        self.edit = edit.View()
        self.tbuffer =  edit.Buffer()
        self.edit.set_buffer(self.tbuffer)
        self.edit.set_wrap_mode(gtk.WrapMode.CHAR)

        self.tbuffer.connect('changed', self.update_cursor_position, self.edit)
        self.edit.set_size_request( 490, 70)
        return self.edit

    def arama(self, widget, *_):
        """
        build search dialog and show
        """
        builder = gtk.Builder()
        builder.add_from_file("../Glade/ara.glade")
        self.search_text  = builder.get_object("entry1")
        self.search_text.set_size_request(170 ,30)
        self.search_text.connect("activate", self.devam)

        self.radio = {i: builder.get_object(f"radiobutton{i}") for i in range(1,4)}

        buton = gtk.Button(" Bul ")
        buton.connect("clicked",self.devam)
        box = builder.get_object("vbox1")
        box.add(buton)
        pencere = builder.get_object("window1")

    #    pencere.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        buffer = self.edit .get_buffer()
        if bounds:=buffer.get_selection_bounds():
            start, end = bounds
            konu = self.edit .get_buffer().get_slice(start, end, widget)
            self.search_text.set_text(konu)
        pencere.show_all()
        self.renk = self.edit .get_buffer().create_tag(background="yellow",foreground="#000000")

    def ara(self,  backward):
        """
        search backward or forward within text buffer
        """
        buffer = self.edit .get_buffer()
        str_text = self.search_text.get_text()
        start, end = buffer.get_bounds()
        buffer.remove_tag(self.renk, start, end)
        iter_ = buffer.get_iter_at_mark(buffer.get_insert())
        i = 0
        if backward:
            while True:
                bul = iter_.backward_search(str_text, gtk.TextSearchFlags.TEXT_ONLY)
                if not bul:
                    break
                match_start, match_end = bul
                i += 1
                buffer.apply_tag(self.renk, match_start, match_end)
                iter_ = match_start
        else:
            while True:
                bul = iter_.forward_search(str_text, gtk.TextSearchFlags.TEXT_ONLY)
                if not bul:
                    break
                match_start, match_end = bul
                i += 1
                buffer.apply_tag(self.renk, match_start, match_end)
                iter_ = match_end

        if not str_text or i < 1:
            ILETI.set_text("Hiçbir Eşleşme Bulunamadı!")
        else:
            ILETI.set_text(f"{i} Tane Eşleşme Bulundu.." )

    def back_ward(self, *_):
        """
		continue seaching value before selection
        """
        buffer = self.edit .get_buffer()
        iter_ = buffer.get_iter_at_mark(buffer.get_insert())
        str_text = self.search_text.get_text()
        start, end = buffer.get_bounds()
        buffer.remove_tag(self.renk, start, end)
        found = iter_.backward_search(str_text, gtk.TextSearchFlags.TEXT_ONLY)
        if found:
            match_start, match_end = found
            buffer.apply_tag(self.renk, match_start, match_end)
            buffer.select_range(match_start, match_end)
            iter_ = match_end
        else:
            ILETI.set_text("Hiçbir Eşleşme Bulunamadı!")

    def devam(self, *_):
        """
        continue seaching value after selection
        """
        for radio in self.radio:
            if self.radio[radio].get_active():
                action, value = radio_action[radio]
                getattr(self, action)(value)

    def get_lines(self, first_y, last_y, buffer_coords, numbers):
        "# Get iter at first y"
        text_view = self.edit
        iter_, _ = text_view.get_line_at_y(first_y)

        # For each iter, get its location and add it to the arrays.
        # Stop when we pass last_y
        count = 0
        while not iter_.is_end():
            width, height = text_view.get_line_yrange(iter_)
            buffer_coords.append(width)
            line_num = iter_.get_line() + 1
            numbers.append(line_num)
            count += 1
            if (width + height) >= last_y:
                break
            iter_.forward_line()
        return count

    def update_cursor_position(self, _, view):
        """
        action for search elements in text
        """
        tabwidth = view.get_tab_width()
        #pos_label = view.get_tab_pos()
        iter_ = self.tbuffer.get_iter_at_mark(self.tbuffer.get_insert())
        row = iter_.get_line() + 1
        start = iter_.copy()
        start.set_line_offset(0)
        col = 0
        while start.compare(iter_) < 0:
            if start.get_char() == '\t':
                col += tabwidth - col % tabwidth
            else:
                col += 1
            start.forward_char()
        STATU.push(False,(f'Sat: {row}, Süt: {col}') )
        if  len(ILETI.get_text()) >= 4:
            ILETI.set_text("")


    def yazdir(self, _, data=False):
        """
        call printing dialog
        """
        window = self.edit.get_toplevel()
        compositor = edit.PrintCompositor().new_from_view(self.edit )
        compositor.set_wrap_mode(gtk.WrapMode.CHAR)
        compositor.set_highlight_syntax(True)
        compositor.set_header_format(False, 'Yazılan Gün  %A', None, '%F')
        filename = f"{data.split(':')[0]}"

        compositor.set_footer_format(True, '%T',
                 f"{os.path.basename(filename)}",
                 'Sayfa %N/%Q')

        compositor.set_print_header(True)
        compositor.set_print_footer(True)

        def begin_print_cb(operation, context, compositor):
            """
			start printing action
			"""
            while not compositor.paginate(context):
                pass
            n_pages = compositor.get_n_pages()
            operation.set_n_pages(n_pages)

        def draw_page_cb(_, context, page_nr, compositor):
            """
			draw current page
			"""
            compositor.draw_page(context, page_nr)

        print_op = gtk.PrintOperation()
        print_op.connect("begin-print", begin_print_cb, compositor)
        print_op.connect("draw-page", draw_page_cb, compositor)
        res = print_op.run(gtk.PrintOperationAction.PRINT_DIALOG, window)

        if res == gtk.PrintOperationResult.ERROR:
            print ("Hatalı Baskı Dosyası:\n\n" + filename)
        elif res == gtk.PrintOperationResult.APPLY:
            print  (f'Baskı Dosyası: "{os.path.basename(filename )}"')
