import os

def source_start(base='', book_id='book'):
    """
    chooses a starting source file in the 'base' directory for id = book_id
    
    """
    repo_htm_path = "{book_id}-h/{book_id}-h.htm".format(book_id=book_id)
    possible_paths = ["book.asciidoc",
                      repo_htm_path,
                      "{}-0.txt".format(book_id),
                      "{}-8.txt".format(book_id),
                      "{}.txt".format(book_id),
                      "{}-pdf.pdf".format(book_id),
                     ]

    # return the first match

    for path in possible_paths:
        fullpath = os.path.join(base, path)
        if os.path.exists(fullpath):
            return path

    return None

