#!/usr/bin/env python

from github3 import login
from secrets import GH_USER, GH_PASSWORD
from sys import argv, exit


LOCATION = {
        'pickle': ('catalog.pickle', 'Pickle of the parsed catalog'),
        'bzip': ('catalog.rdf.bz2', 'bzipped version of the catalog'),
        'rdf': ('index/catalog.rdf', 'RDF version of the catalog'),
        }

EXISTING = {
        'pickle': 0,
        'bzip': 0,
        'rdf': 0
        }


def authenticate():
    return login(GH_USER, GH_PASSWORD)


def upload_files(repo):
    #r = session.repository('sethwoodworth', 'GITenberg')
    for k in LOCATION:
        dl = repo.create_download(k, *LOCATION[k])
        if dl:
            EXISTING[k] = dl.id
            print("File {0} uploaded.".format(dl.name))
        else:
            print("ERROR: File {0} was not uploaded.".format(LOCATION[k][0]))
    write_config()


def delete_existing(repo):
    for k in EXISTING:
        if not EXISTING[k]:
            return

        dl = repo.download(EXISTING[k])
        if dl.delete():
            print("File {0} deleted.".format(dl.name))
        else:
            print("ERROR: File {0} was not deleted.".format(dl.name))


def update_old_files(repo):
    delete_existing(repo)
    upload_files(repo)


def read_config():
    with open('docs/download_ids') as fd:
        for line in fd:
            name, dl_id = line.split(': ')
            dl_id = int(dl_id)
            if name in EXISTING and dl_id > 0:
                EXISTING[name] = int(dl_id)


def write_config():
    with open('docs/download_ids', 'w') as fd:
        for k in EXISTING:
            fd.write('{0}: {1}'.format(k, EXISTING[k]))


commands = {
        'upload': upload_files,
        'delete': delete_existing,
        'update': update_old_files,
        }


def main():
    if not argv[1:]:
        print("Usage {0}: upload | delete | update\n")
        exit(0)
    elif argv[1] in commands:
        read_config()
        g = authenticate()
        #r = g.repository('sethwoodworth', 'GITenberg')
        r = g.repository('sigmavirus24', 'GITenberg')
        commands[argv[1]](r)


if __name__ == '__main__':
    main()
