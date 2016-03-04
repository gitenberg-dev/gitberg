# coding=utf-8
# mostly constants related to Creative Commons
# let's be DRY with these parameters

## need to add versioned CC  entries

INFO_CC = (
    ('CC BY-NC-ND', 'by-nc-nd', 'Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported (CC BY-NC-ND 3.0)', 'http://creativecommons.org/licenses/by-nc-nd/3.0/', 'Creative Commons Attribution-NonCommercial-NoDerivs'),     
    ('CC BY-NC-SA', 'by-nc-sa', 'Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)', 'http://creativecommons.org/licenses/by-nc-sa/3.0/', 'Creative Commons Attribution-NonCommercial-ShareAlike'),
    ('CC BY-NC', 'by-nc', 'Creative Commons Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0)', 'http://creativecommons.org/licenses/by-nc/3.0/', 'Creative Commons Attribution-NonCommercial'),
    ('CC BY-ND', 'by-nd', 'Creative Commons Attribution-NoDerivs 3.0 Unported (CC BY-ND 3.0)', 'http://creativecommons.org/licenses/by-nd/3.0/','Creative Commons Attribution-NoDerivs'), 
    ('CC BY-SA', 'by-sa', 'Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)', 'http://creativecommons.org/licenses/by-sa/3.0/', 'Creative Commons Attribution-ShareAlike'),
    ('CC BY', 'by', 'Creative Commons Attribution 3.0 Unported (CC BY 3.0)', 'http://creativecommons.org/licenses/by/3.0/', 'Creative Commons Attribution'), 
    ('CC0', 'cc0', 'No Rights Reserved (CC0)', 'http://creativecommons.org/about/cc0', 'No Rights Reserved (CC0)'),
)
INFO_FREE = INFO_CC + (
    ('GFDL', 'gdfl', 'GNU Free Documentation License', 'http://www.gnu.org/licenses/fdl-1.3-standalone.html', 'GNU Free Documentation License'),
    ('LAL', 'lal', 'Licence Art Libre', 'http://artlibre.org/licence/lal/', 'Licence Art Libre'),
)
INFO_PD = (
    ('PD-US', 'pd-us', 'Public Domain, US', 'http://creativecommons.org/about/pdm', 'Public Domain, US'),
)
INFO_ALL = INFO_FREE + INFO_PD
# CCHOICES, CCGRANTS, and FORMATS are all used in places that expect tuples
# CONTENT_TYPES will be easiest to manipulate in ungluify_record as a dict

CCCHOICES = tuple([(item[0],item[2]) for item in INFO_CC])
FREECHOICES = tuple([(item[0],item[2]) for item in INFO_FREE])
    
CHOICES = tuple([(item[0],item[4]) for item in INFO_ALL])

CCGRANTS = tuple([(item[0],item[3]) for item in INFO_CC])

GRANTS = tuple([(item[0],item[3]) for item in INFO_ALL])

LICENSE_LIST =  [item[0] for item in INFO_CC]
LICENSE_LIST_ALL =  [item[0] for item in INFO_ALL]
FACET_LIST = [item[1] for item in INFO_ALL] 

RIGHTS_ALIAS = {
    "Public domain in the USA.":"PD-US",
    }


class CCLicense():
    @staticmethod
    def url(license):
        license = RIGHTS_ALIAS.get(license, license)
        if license in LICENSE_LIST_ALL:
            return INFO_ALL[LICENSE_LIST_ALL.index(license)][3]
        else:
            return ''

    @staticmethod
    def badge(license):
        if license == 'PD-US':
            return '/static/images/pdmark.png'
        elif license == 'CC0':
            return '/static/images/cc0.png'
        elif license == 'CC BY':
            return '/static/images/ccby.png'
        elif license == 'CC BY-NC-ND':
            return '/static/images/ccbyncnd.png'
        elif license == 'CC BY-NC-SA':
            return '/static/images/ccbyncsa.png'
        elif license == 'CC BY-NC':
            return '/static/images/ccbync.png'
        elif license == 'CC BY-SA':
            return '/static/images/ccbysa.png'
        elif license == 'CC BY-ND':
            return '/static/images/ccbynd.png'
        elif license == 'GFDL':
            return '/static/images/gfdl.png'
        elif license == 'LAL':
            return '/static/images/lal.png'
        else:
            return ''

def description(license):
        if license == 'PD-US':
            return 'Use of this material is not restricted by copyright in the US.'
        elif license == 'CC0':
            return 'The copyright owner has dedicated the material to the public domain by waiving all of his or her rights to the work worldwide under copyright law, including all related and neighboring rights, to the extent allowed by law. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.'
        elif license == 'CC BY':
            return 'You are free to: copy and redistribute the material in any medium or format; remix, transform, and build upon the material; for any purpose, even commercially. Under the following terms: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.'
        elif license == 'CC BY-NC-ND':
            return 'You are free to: copy and redistribute the material in any medium or format; under the following terms: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.; you may not use the material for commercial purposes; if you remix, transform, or build upon the material, you may not distribute the modified material.'
        elif license == 'CC BY-NC-SA':
            return 'You are free to: copy and redistribute the material in any medium or format; remix, transform, and build upon the material; Under the following terms: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. You may not use the material for commercial purposes. If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.'
        elif license == 'CC BY-NC':
            return 'You are free to: copy and redistribute the material in any medium or format; remix, transform, and build upon the material; under the following terms: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. You may not use the material for commercial purposes.'
        elif license == 'CC BY-SA':
            return 'You are free to: copy and redistribute the material in any medium or format; remix, transform, and build upon the material; for any purpose, even commercially. Under the following terms: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.'
        elif license == 'CC BY-ND':
            return 'You are free to: copy and redistribute the material in any medium or format; for any purpose, even commercially. Under the following terms: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. If you remix, transform, or build upon the material, you may not distribute the modified material.'
        elif license == 'GFDL':
            return 'The purpose of this License is to make a manual, textbook, or other functional and useful document "free" in the sense of freedom: to assure everyone the effective freedom to copy and redistribute it, with or without modifying it, either commercially or noncommercially. Secondarily, this License preserves for the author and publisher a way to get credit for their work, while not being considered responsible for modifications made by others.'
        elif license == 'LAL':
            return 'Avec la Licence Art Libre, l\'autorisation est donnée de copier, de diffuser et de transformer librement les œuvres dans le respect des droits de l\'auteur.'
        else:
            return ''

class ccinfo():
    def __init__(self, license):
        value=license_value(license)
        self.license=value if value else license
    
    @property
    def description(self):
        return description(self.license)
    @property
    def badge(self):
        return CCLicense.badge(self.license)
    @property
    def url(self):
        return CCLicense.url(self.license)
    @property
    def full_title(self):
        if self.license in LICENSE_LIST_ALL:
            return INFO_ALL[LICENSE_LIST_ALL.index(self.license)][2]
        else:
            return self.license
    @property
    def title(self):
        if self.license in LICENSE_LIST_ALL:
            return INFO_ALL[LICENSE_LIST_ALL.index(self.license)][4]
        else:
            return self.license
    @property
    def is_cc(self):
        return self.license in LICENSE_LIST
    @property
    def is_pd(self):
        return self.license == 'PD-US'
        
    def __str__(self):
        return self.license

def license_value(facet):
    if facet in FACET_LIST:
        return LICENSE_LIST_ALL[FACET_LIST.index(facet)]
    else:
        return ''
