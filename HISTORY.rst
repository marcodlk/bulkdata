=======
History
=======


0.4.0 (2020-04-10)
------------------

* First release.


0.5.3 (2020-04-14)
------------------

* Fixes some bugs in the Card class.

* Expanded documentation on:
    - usage
    - API
        * Card class
        * Deck class


0.6.0 (2020-04-23)
------------------

* Sorting deck cards is now possible with `Deck.sort` method.

* Dumping cards containing trailing blank fields no longer 
  creates blank continuation lines, as trailing blank fields
  are ignored when converting card to string.