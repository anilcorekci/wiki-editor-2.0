#!/bin/python3
# -*- coding: utf-8 -*-
"""Wiki Editor özgür bir yazılımdır, onu Özgür Yazılım
Vakfı'nın yayınladığı GNU Genel Kamu Lisansı'nın 2.
sürümü veya (tercihinize bağlı) daha sonraki sürümleri
altında dağıtabilir ve/veya değiştirebilirsiniz.

Wiki Editor  faydalı olacağı umut edilerek dağıtılmaktadır,
fakat HİÇBİR GARANTİSİ YOKTUR; hatta ÜRÜN DEĞERİ
ya da BİR AMACA UYGUNLUK gibi garantiler de
vermez. Lütfen GNU Genel Kamu Lisansı'nı daha fazla
ayrıntı için inceleyin."""

import sys
import notebook as pen
import gi
from gi.repository import Gtk as gtk
gi.require_version('Gtk', '3.0')

HITO = pen.WikiEditor()
if __name__ == '__main__':
    if len(sys.argv) < 2:
        HITO.yeni(False)
    else:
        DOSYA = sys.argv[1]
        HITO.yeni(DOSYA)
        HITO.open(DOSYA)
    gtk.main()
