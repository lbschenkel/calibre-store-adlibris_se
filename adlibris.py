# -*- coding: utf-8 ts=4 sw=4 sts=4 et -*-
from __future__ import (absolute_import, print_function, unicode_literals)

__license__   = 'GPL 3'
__copyright__ = '2017, Leonardo Brondani Schenkel <leonardo@schenkel.net>'
__docformat__ = 'restructuredtext en'

import urllib

from PyQt5.Qt import QUrl
from contextlib import closing
from lxml import html

from calibre import browser
from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.basic_config import BasicStoreConfig
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog

if __name__ == '__main__':
    from lib import GenericStore, xpath, text
else:
    from calibre_plugins.lbschenkel_store_adlibris_se.lib import GenericStore, xpath, text

class AdlibrisStore(GenericStore):
    url                = 'https://www.adlibris.com/se'
    search_url         = '{0}/sok?filter=format_sv:e-bok&q={1}&ps={2}'
    words_drm_locked   = ['drm']
    words_drm_unlocked = ['vattenmärkt']

    def find_search_results(self, doc):
        return xpath(doc, '//*[@itemtype="https://schema.org/Book"]')

    def find_book_details(self, doc):
        details = self.find_search_results(doc)
        if len(details) > 0:
            return details[0]
        else:
            return details

    def parse_search_result(self, node):
        r = SearchResult()
        r.detail_item = text(node, './/*', 'item-info', '/a/@href')
        r.title       = text(node, './/*[@itemprop="name"]')
        r.author      = text(node, './/*[@itemprop="author"]')
        r.price       = text(node, './/*', 'current-price')
        r.formats     = text(node, './/*', 'format ')
        r.cover_url   = text(node, './/img[@itemprop="image"]', '', '/@data-original')
        return r

    def parse_book_details(self, node):
        r = SearchResult()
        r.title     = text(node, './/*[@itemprop="name"]')
        r.author    = text(node, './/*[@itemprop="author"]')
        r.price     = text(node, './/*', 'current-price')
        r.cover_url = text(node, './/img[@itemprop="image"]', '', '/@src')
        r.formats   = text(node, './/li[contains(., "elektroniska format:")]/*', 'product-info-panel__attributes__value', '/text()')
        r.drm       = r.formats
        return r

    def normalize_formats(self, text):
        upper = text.strip().upper()
        formats = []
        if 'EPUB' in upper:
            formats.append('EPUB')
        if 'PDF' in upper:
            formats.append('PDF')
        if formats:
            return ', '.join(formats)
        else:
            return text


def build_details(doc):
    drm     = None
    for format in formats:
        if 'DRM' in format:
            drm = SearchResult.DRM_LOCKED
        elif 'vatten' in format.lower():
            drm = SearchResult.DRM_UNLOCKED

    def to_format(f):
        f = f.strip()
        if f.upper().startswith('PDF'):
            return 'PDF'
        elif f.upper().startswith('EPUB'):
            return 'EPUB'
        else:
            return '?'
    formats = sorted(set(map(to_format, formats)))

class AdlibrisStorePlugin(StorePlugin):
    store = AdlibrisStore()

    def search(self, query, max_results, timeout):
        return self.store.search(query, max_results, timeout)

    def get_details(self, result, timeout):
        return self.store.get_details(result, timeout)

    def open(self, parent, item, external):
        return self.store.open(self.name, self.gui, parent, item, external)

    def create_browser(self):
        return self.store.create_browser()

if __name__ == '__main__':
    import sys
    query   = ' '.join(sys.argv[1:])
    max     = 3
    timeout = 10

    store = AdlibrisStore()
    for r in store.search(query, max, timeout):
        print(r)
        store.get_details(r, timeout)
        print(r)
        print("---")
