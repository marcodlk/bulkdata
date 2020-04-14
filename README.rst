========================
Bulk Data Python Package
========================


.. image:: https://img.shields.io/pypi/v/bulkdata.svg
        :target: https://pypi.python.org/pypi/bulkdata

.. image:: https://img.shields.io/travis/marcodlk/bulkdata.svg
        :target: https://travis-ci.com/marcodlk/bulkdata

.. image:: https://readthedocs.org/projects/bulkdata/badge/?version=latest
        :target: https://bulkdata.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/marcodlk/bulkdata/shield.svg
     :target: https://pyup.io/repos/github/marcodlk/bulkdata/
     :alt: Updates



Bulk Data Python Package makes it easy to create and manipulate bulk 
data files.


* Free software: MIT license
* Documentation: https://bulkdata.readthedocs.io.


Features
--------

* ``Card`` objects represent Bulk Data Cards; functionally similar to 
  ``list`` objects but can be serialized to a bulk data formatted string
  representing the card.

* No explicit Bulk Data Card definitions are necessary.

* ``Deck`` objects represent a Bulk Data "Deck" containing Bulk Data Cards
  that can be added, edited, or deleted.

* Loading BDF files containing mixed formatting is supported.

* Bulk Data Formats currently supported:
   * Fixed (same as Small in NASTRAN)
   * Free


Example
-------

This a quick example of using the ``bulkdata`` package to update a BDF file.

.. code-block:: python

    from bulkdata import Deck, Card

    bdf_filename = BDF_DIR + "/example.bdf"

    # load Deck from BDF file
    with open(bdf_filename) as bdf_file:
        deck = Deck.load(bdf_file)

    # CORD2R variables
    cid = 1
    rid = None
    a = [-2.9, 1.0, 0.0]
    b = [3.6, 0.0, 1.0]
    c = [5.2, 1.0, -2.9]

    # create CORD2R card
    cord2r = Card("CORD2R")
    cord2r.append(cid)
    cord2r.append(rid)
    cord2r.extend(a)
    cord2r.extend(b)
    cord2r.extend(c)

    # print the CORD2R card in fixed format (the default)
    print("-- CORD2R fixed formatting --")
    print(cord2r.dumps("fixed"))

    # print the CORD2R card in free format
    print("-- CORD2R free formatting --")
    print(cord2r.dumps("free"))

    # add card to the deck
    deck.append(cord2r)

    # get AEROZ card
    aeroz = deck.find_one({"name": "AEROZ"})

    print("-- AEROZ before update --")
    print(aeroz.dumps())

    # update the ACSID field (first one)
    aeroz[0] = cid

    # update mass and length units fields while we're at it
    aeroz[[3, 4]] = ["N", "M"] 

    print("-- AEROZ after update --")
    print(aeroz.dumps())

    # dump Deck to update BDF file
    with open(bdf_filename, "w") as f:
        deck.dump(f)

Output::
   
   -- CORD2R fixed formatting --
   CORD2R  1               -2.9    1.      0.      3.6     0.      1.      +0      
   +0      5.2     1.      -2.9
   
   -- CORD2R free formatting --
   CORD2R,1, ,-2.9,1.,0.,3.6,0.,1.,+0
   +0,5.2,1.,-2.9
   
   -- AEROZ before update --
   AEROZ           YES     NO      SLIN    IN      400.    300     12000.  +0      
   +0      10.     0.      0.
   
   -- AEROZ after update --
   AEROZ   1       YES     NO      N       M       400.    300     12000.  +0      
   +0      10.     0.      0.

For a more detailed overview check out the 
`documentation <https://bulkdata.readthedocs.io>`_ and/or the 
`bulkdata-usage <https://github.com/marcodlk/bulkdata/blob/master/examples/bulkdata-usage.ipynb>`_
notebook.

TODO
----

* Add support for BDF files containing INCLUDE statements.
* Add support for Large Field entries
* Add support for BDF files with tabs?

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage