# -*- coding: utf-8 ts=4 sw=4 sts=4 et -*-
from __future__ import (absolute_import, print_function, unicode_literals)

__license__     = 'GPL 3'
__copyright__   = '2017, Leonardo Brondani Schenkel <leonardo@schenkel.net>'
__docformat__   = 'restructuredtext en'

from calibre.customize import StoreBase

class AdlibrisStore(StoreBase):
    name            = 'Adlibris.se'
    version         = (2025, 3, 0)
    description     = 'Handla böcker, skönlitteratur och facklitteratur hos Adlibris bokhandel. Priserna ligger lägst på marknaden vilket har noterats i ett flertal test i media.'
    author          = 'Leonardo Brondani Schenkel <leonardo@schenkel.net>'
    actual_plugin   = 'calibre_plugins.lbschenkel_store_adlibris_se.adlibris:AdlibrisStorePlugin'
    headquarters    = 'SE'
    formats         = ['EPUB', 'PDF']

