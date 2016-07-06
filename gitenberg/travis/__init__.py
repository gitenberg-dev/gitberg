import subprocess
import uuid
import os

BUILD_EPUB_SCRIPT = """
#!/bin/sh

function build_epub_from_asciidoc {

	asciidoctor -a toc,idprefix=xx_,version=$1 -b xhtml5 -T ./asciidoctor-htmlbook/htmlbook-autogen/ -d book book.asciidoc -o book.html
	git clone https://github.com/gitenberg-dev/HTMLBook

	# make book.html available to jinja2 environment by putting it into templates
	cp book.html asciidoctor-htmlbook/gitberg-machine/templates/

	/usr/bin/python asciidoctor-htmlbook/gitberg-machine/machine.py -o . -m metadata.yaml book.html
	xsltproc -stringparam external.assets.list " " ./HTMLBook/htmlbook-xsl/epub.xsl book.html
	cp ./HTMLBook/stylesheets/epub/epub.css OEBPS
	if [ -e cover.jpg ]; then cp cover.jpg OEBPS/cover.jpg; fi

	# look for first images directory and one found, copy over to ./OEBPS
	find . -name images -type d | head -n 1 | xargs -I {} mv {} ./OEBPS/
	zip -rX book.epub mimetype
	zip -rX book.epub OEBPS/ META-INF/
	if test -d "OEBPS/images/"; then zip -rX book.epub OEBPS/images/ ;fi
	if [ "$2" != "book" ]; then mv book.epub $2.epub; fi    

} 

build_epub_from_asciidoc $1 $2
"""


def build_epub_from_asciidoc (version, epub_title):
	"""
	build for asciidoctor input
	"""

	fname = "{}.sh".format(uuid.uuid4())

	try:
	    f = open(fname, "wb")
	    f.write(BUILD_EPUB_SCRIPT.encode('utf-8'))
	    f.close()
	    os.chmod(fname, 0755)

	    output = subprocess.check_output("./{fname} {version} {epub_title}".format(fname=fname, 
	    	  version=version, epub_title=epub_title), 
	    	  shell=True)
	    print (output)
	except Exception as e:
	    print (e)
	finally:
	    os.remove(fname)