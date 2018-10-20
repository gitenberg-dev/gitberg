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

def get_wd_id(pg_id):
    pg_id = str(pg_id)
    return _table.get(pg_id, None)

def get_pg_summary(pg_id):
    return get_item_summary(get_wd_id(pg_id))

def get_pg_links(pg_id):
    return get_links(get_wd_id(pg_id))
    
try:
    pg_wd_file =  requests.get('https://raw.githubusercontent.com/gitenberg-dev/pg-wikipedia/master/pg-wd.csv')
    csvreader= csv.reader(pg_wd_file.iter_lines(),delimiter=',', quotechar='"')
except requests.ConnectionError:
    csvreader =  []
for (pg_id,wd_id) in csvreader:
    _table[pg_id]=wd_id
