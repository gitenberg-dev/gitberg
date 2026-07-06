# from https://github.com/gitenberg-dev/pg-wikipedia

from wikipedia import wikipedia
from wikipedia.exceptions import (PageError,WikipediaException,DisambiguationError)

import csv
import requests
import logging

logger = logging.getLogger(__name__)

_table={}
def get_item_summary(wd_id, lang='en'):
    if wd_id is None:
        return None
    try:
        r = requests.get(u'https://www.wikidata.org/wiki/Special:EntityData/{}.json'.format(wd_id))
    except:
        logger.warning( u"couldn't get https://www.wikidata.org/wiki/Special:EntityData/{}.json".format(wd_id))
        return ""
    try:
        title = r.json()['entities'][wd_id]['sitelinks']['{}wiki'.format(lang)]['title']
        try:
            return wikipedia.summary(title)
        except (PageError,WikipediaException,DisambiguationError):
            logger.warning(u"couldn't get wikipedia.summary({})".format(title))
            return ''
    except ValueError:
        #not JSON
        return ""
    except KeyError:
        logger.warning(u"couldn't get wikidata key {}".format(wd_id))
        return ""

def get_links(wd_id):
    r = requests.get(u'https://www.wikidata.org/wiki/Special:EntityData/{}.json'.format(wd_id))
    try:
        sitelinks = r.json()['entities'][wd_id]['sitelinks'].values()
        return [sitelink['url'] for sitelink in sitelinks]
    except ValueError:
        #not JSON
        return ""

PG_WD_URL = 'https://raw.githubusercontent.com/gitenberg-dev/pg-wikipedia/master/pg-wd.csv'
_table_loaded = False

def _load_table():
    """Lazily fetch the PG id -> Wikidata id mapping (one attempt per process).

    This used to happen at import time, which meant any application importing
    the gitenberg package performed a network fetch just to load its code —
    and a bad response (rate-limited/error/truncated, i.e. anything that isn't
    the expected 2-column CSV) raised out of the import and left the importing
    process broken. Under mod_wsgi that poisoned a web worker into serving
    only 500s until manually killed (Gluejar/regluit#1204, 2026-07-06).

    Now the fetch happens on first lookup, failures are logged and tolerated
    (lookups just return None), and malformed rows are skipped.
    """
    global _table_loaded
    if _table_loaded:
        return
    _table_loaded = True  # one attempt per process, success or not
    try:
        pg_wd_file = requests.get(PG_WD_URL, timeout=10)
        if pg_wd_file.status_code != 200:
            logger.warning(u"couldn't load %s: HTTP %s", PG_WD_URL, pg_wd_file.status_code)
            return
        lines = (line.decode('utf-8') for line in pg_wd_file.iter_lines())
        for row in csv.reader(lines, delimiter=',', quotechar='"'):
            if len(row) == 2:
                _table[row[0]] = row[1]
            elif row:
                logger.warning(u"skipping malformed row in pg-wd.csv: %r", row)
    except Exception:
        logger.warning(u"couldn't load %s", PG_WD_URL, exc_info=True)

def get_wd_id(pg_id):
    _load_table()
    pg_id = str(pg_id)
    return _table.get(pg_id, None)

def get_pg_summary(pg_id):
    return get_item_summary(get_wd_id(pg_id))

def get_pg_links(pg_id):
    return get_links(get_wd_id(pg_id))
    
