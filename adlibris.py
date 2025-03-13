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

import json
import re

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
        # This finds the *variants*, not the *books*, as each "row" may contain
        # multiple variants with their own format/price/etc.:
        return xpath(doc, '//*[@class="search-result__list-view__product__wrapper" and @data-isbook="True"]//*[@class="variant"]')

    def parse_search_result(self, variant):
        # Look at the ancestor to find the book:
        book = xpath(variant, './ancestor::*[@class="search-result__list-view__product__wrapper" and @data-isbook="True"]')[0]
        
        r = SearchResult()
        r.detail_item = text(variant, './/a[1]', None, '/@href')
        r.price       = text(variant, './/*', 'price sek', joiner=' ')
        r.title       = text(book, './/a', 'search-result__product__name')
        r.author      = text(book, './/*[@itemprop="author"]')
        r.cover_url   = text(book, './/img[@itemprop="image"]/@data-src', '', '')
        return r

    def find_book_details(self, variant):
        # The book details are not in the HTML, but in a JS (JSON) variable
        # inside a script tag.
        scripts = xpath(variant, '//script', None, '/text()')
        for script in scripts:
            match = re.search('pageData = ({.+});', script)
            if match:
                data = json.loads(match.group(1))
                data = data['ProductVariants'][0] # details page should always be for single variant
                return data
        raise Exception('Cannot find book details')

    def parse_book_details(self, data):
        r = SearchResult()
        r.title     = data['Title']
        r.author    = ' & '.join(data['Authors'] or [])
        r.formats   = data['ProductInfo']['EBookVersion']['Values'][0]['Value']
        r.drm       = r.formats
        return r

    def normalize_formats(self, text):
        text = text.lower()
        if text.startswith('epub') or text.startswith('enhanced epub'):
            return 'EPUB'
        if text.startswith('pdf'):
            return 'PDF'
        return super().normalize_formats(text)


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
    max     = 10
    timeout = 10

    store = AdlibrisStore()
    for r in store.search(query, max, timeout):
        print(r)
        store.get_details(r, timeout)
        print(r)
        print("---")
