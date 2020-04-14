=====
Usage
=====

The :mod:`bulkdata` package loads BDF files into memory as
:class:`~bulkdata.deck.Deck` objects, which are collections of
:class:`~bulkdata.card.Card` objects. This page will
demonstrate how to create, modify, and utilize these objects.

Card
----

Build card
^^^^^^^^^^

First, let's initialize a :class:`~bulkdata.card.Card` object
with name "EXAMPLE".

.. code-block:: python

    from bulkdata import Card

    card = Card("EXAMPLE")

At this point, the card only has a name and no fields. If we dump the 
card to its string representation in *fixed* format with 
:meth:`~bulkdata.card.Card.dumps`, we get:

.. code-block:: python

    print(card.dumps("fixed"))

.. code-block:: none

    EXAMPLE

That's not very useful, let's enter some fields into the card.

.. code-block:: python

    # append integer field
    card.append(100)

    # append real field
    card.append(3.14)

    # append character field
    card.append("string")

Now if we look at the card's string representation we see:

.. code-block:: python

    print(card.dumps("fixed"))

.. code-block:: none

    EXAMPLE 100     3.14    string

We can also enter blank fields.

.. code-block:: python

    # append a blank field using None
    card.append(None)

    # append a blank field using null string
    card.append("")

    # trailing blank fields are ingored during `dumps` call, 
    # so printing the card here yields the same result as the
    # previous print
    print(card.dumps("fixed"))

.. code-block:: none

    EXAMPLE 100     3.14    string


Using the :meth:`~bulkdata.card.Card.append` method, we entered one
field at a time. But what if we want to enter a list of fields?
This is done with the :meth:`~bulkdata.card.Card.extend` method:

.. code-block:: python

    # append a list of integer fields
    card.extend([0, 1, 2, 3, 4])

    # NOTE: blank fields are there
    print(card.dumps("fixed"))

.. code-block:: none

    EXAMPLE 100     3.14    string                  0       1       2       +0      
    +0      3       4


Sometimes, field entries span across two fields to allow more
characters (this is particularly common in **ZAERO**, where the
*Large Field* format doesn't exist). Since it's technically a
single entry, we use the :meth:`~bulkdata.card.Card.append` method
to do this while specifying the need for 2 fields, instead of
the default 1.

.. code-block:: python

    # append a character field spanning 2 field cells
    card.append("thisislongstring", fieldspan=2)

    print(card.dumps("fixed"))

.. code-block:: none

    EXAMPLE 100     3.14    string                  0       1       2       +0      
    +0      3       4       thisislongstring


There are also times when two lists of field entries have alternating
positions in the card. In this case, the easiest way to enter the
fields is with a little help from the builtin ``zip`` function.

.. code-block:: python

    # append two field lists, alternating
    numbers = [42, -9.99999e9, 10000000, -.0000000001]
    strings = ["one", "two", "three", "four"]
    for number, string in zip(numbers, strings):
        card.append(number)
        card.append(string)

    print(card.dumps("fixed"))

.. code-block:: none

    EXAMPLE 100     3.14    string                  0       1       2       +0      
    +0      3       4       thisislongstring42      one     -10.+9  two     +1      
    +1      10000000three   -1.-10  four


And if each field entry spans across two fields:

.. code-block:: python

    for longstring in ["123456789", "helloworld"]:
        card.append(longstring, fieldspan=2)

    print(card.dumps("fixed"))

.. code-block:: none

    EXAMPLE 100     3.14    string                  0       1       2       +0      
    +0      3       4       thisislongstring42      one     -10.+9  two     +1      
    +1      10000000three   -1.-10  four    123456789       helloworld


By the way, we can also get the card's *free* format representation:

.. code-block:: python

    print(card.dumps("free"))

.. code-block:: none

    EXAMPLE,100,3.14,string, , ,0,1,2,+0
    +0,3,4,thisislo,ngstring,42,one,-10.+9,two,+1
    +1,10000000,three,-1.-10,four,12345678,9,hellowor,ld


Printing the card object uses the :meth:`~bulkdata.card.Card.dumps`
method, which defaults to *fixed* format if no format argument is
provided.

.. code-block:: python

    # these are all analogous

    # print(card.dumps("fixed"))
    # print(card.dumps())
    print(card)

.. code-block:: none

    EXAMPLE 100     3.14    string                  0       1       2       +0      
    +0      3       4       thisislongstring42      one     -10.+9  two     +1      
    +1      10000000three   -1.-10  four    123456789       helloworld


Modify card
^^^^^^^^^^^

One of the main benefits of :mod:`bulkdata` is the ability to edit
existing cards, agnostic to card definitions and/or how
the card was built.

Let's make some edits to the card we created to demonstrate what
we mean. First, a simple edit to the first field of the card.

.. code-block:: python

    # set first field value to 99
    print("First field current:", card[0])

    card[0] = 99

    print("First field set to 99:", card[0])

    # increment first field value by 100
    card[0] += 100

    print("First field increment by 100:", card[0])

.. code-block:: none

    First field current: 100
    First field set to 99: 99
    First field increment by 100: 199

Now let's update the two blank fields we set earlier to contain
a character entry spanning two fields.

.. code-block:: python

    # the blank fields are at index 3 and 4
    print("Blank fields:", card[[3, 4]])

    card[[3, 4]] = "newstr"

    print("One field no longer blank:", card[[3, 4]])

    card[[3, 4]] = "newlongstring"

    print("Both fields no longer blank:", card[[3, 4]])

.. code-block:: none

    Blank fields: ['', '']
    One field no longer blank: ['newstr', '']
    Both fields no longer blank: ['newlongs', 'tring']

Note that when we specify several indexes during the set operation,
every field at that index will be cleared to make way for the new
value; if the new field value does not cover every field, the
leftover fields will remain blank after the set.
In the first set above, the "newstr" did not require two fields,
but because we specified that both index 3 and 4 fields were being
set, the second field (at index 4) remained blank after.

This should clarify that the way fields are entered does not matter,
internally the card maintains a value for each field cell.
The :class:`~bulkdata.card.Card` object handles the conversion of field
inputs to the appropriate field cells according to the specified
operation.

Let's do a similar operation but with a list of new field values
and indexing the set operation with slice syntax.

.. code-block:: python

    # we will overwrite the fields from index 10 to 16 (excluding 16)
    print("Fields to overwrite:", card[10:16])

    card[10:16] = [5, 6, 7, 8, 9]

    print("Fields after set:", card[10:16])

.. code-block:: none

    Fields to overwrite: ['thisislo', 'ngstring', 42, 'one', -10000000000.0, 'two']
    Fields after set: [5, 6, 7, 8, 9, '']

To remove fields, we can use the :meth:`~bulkdata.card.Card.pop` 
method the remove the last field...

.. code-block:: python

    print("Last line before pop:", card[16:])

    popped_field = card.pop()

    print("Popped field:", popped_field)
    print("Last line after pop:", card[16:])

.. code-block:: none

    Last line before pop: [10000000, 'three', -1e-10, 'four', 12345678, 9, 'hellowor', 'ld']
    Popped field: ld
    Last line after pop: [10000000, 'three', -1e-10, 'four', 12345678, 9, 'hellowor']

... or builtin ``del`` to remove at specified index(s)...

.. code-block:: python

    # delete first item of last (3rd) line
    del card[16]

    print("Last line after delete first:", card[16:])

    # delete remaining first two items of last line
    del card[16:18]

    print("Last line after delete remaining first & second:", card[16:])

.. code-block:: none

    Last line after delete first: ['three', -1e-10, 'four', 12345678, 9, 'hellowor']
    Last line after delete remaining first & second: ['four', 12345678, 9, 'hellowor']

... or :meth:`~bulkdata.card.Card.resize`, which removes fields
(or appends blank fields) until the specified size is reached.

.. code-block:: python

    card.resize(16)

    print("Last line after resize:", card[16:])
    print("Number of fields:", len(card))

.. code-block:: none

    Last line after resize: []
    Number of fields: 16

After these modifications, we can see that the card has been updated:

.. code-block:: python

    print(card)

.. code-block:: none

    EXAMPLE 199     3.14    string  newlongstring   0       1       2       +0      
    +0      3       4       5       6       7       8       9

The card is functionally analogous to a ``list`` of field values.

.. code-block:: python

    print("Number of fields:", len(card))
    print("Card field values:", card[:])

.. code-block:: none

    Number of fields: 16
    Card field values: [199, 3.14, 'string', 'newlongs', 'tring', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, '']


Alternate way of building a card
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If we have an idea of how many fields we need, we can alternatively
initialize the card with a specified number of blank fields and
then overwrite the fields with set operations, instead of using
:meth:`~bulkdata.card.Card.append` and/or
:meth:`~bulkdata.card.Card.extend`.

.. code-block:: python

    # if we don't know the exact number of fields, 
    # we can overestimate for now and remove the excess later
    numfields = 100
    card = Card("EXAMPLE", size=numfields)

    # indeed, our card has 100 fields
    print(len(card))

.. code-block:: none

    100

Let's make this card just like the one from the `Build card`_ section.

.. code-block:: python

    # set integer field
    card[0] = 100

    # set real field
    card[1] = 3.14

    # set character field
    card[2] = "string"

    # # set blank field using None
    # card[3] = None

    # # set blank field using null string
    # card[4] = ""

    # ^ that would be redundant, fields are already blank

    # set list of integer fields
    card[5:10] = [0, 1, 2, 3, 4]

    # set character field spanning 2 field cells
    card[10:12] = "thisislongstring"

    # set two field lists, alternating
    numbers = [42, -9.99999e9, 10000000, -.0000000001]
    strings = ["one", "two", "three", "four"]
    card[12:20:2] = numbers
    card[13:20:2] = strings

    # set field list with fields spanning 2 field cells
    for i, longstring in enumerate(["123456789", "helloworld"]):
        i0 = 20 + 2*i
        i1 = i0 + 2
        card[i0:i1] = longstring

    # remove the trailing blank fields
    print("Number of fields before strip:", len(card))
    card.strip()
    print("Number of fields after strip:", len(card))

.. code-block:: none

    Number of fields before strip: 100
    Number of fields after strip: 24

The string representation of the card should look familar.

.. code-block:: python

    print(card)

.. code-block:: none

    EXAMPLE 100     3.14    string                  0       1       2       +0      
    +0      3       4       thisislongstring42      one     -10.+9  two     +1      
    +1      10000000three   -1.-10  four    123456789       helloworld


For more information on the :class:`~bulkdata.card.Card` class,
check out the API documentation.

Deck
----

The main utility of :mod:`bulkdata` is the ability to load an entire
BDF file into memory and update it with minimal effort, agnostic
to any specifications of the included cards. For this purpose,
:mod:`bulkdata` provides the :class:`~bulkdata.deck.Deck` class.

Build deck
^^^^^^^^^^

Let's initialize a :class:`~bulkdata.deck.Deck` object and add
some cards.

.. code-block:: python

    from bulkdata import Deck

    deck = Deck()

    # add slight variations of the original card we created in the above section
    orig_card_str = card.dumps()
    for i in range(8):
        # load new card from original card string
        card_var = Card.loads(orig_card_str)
        # just first line
        card_var.resize(8)
        # change name
        card_var.name = "EXAMPL" + str(i)
        # change first field
        card_var[0] += 1
        # change field i
        card_var[i] = "EDITED"
        deck.append(card_var)

The deck is functionally analogous to a ``list`` of cards.

.. code-block:: python

    print("Number of cards:", len(deck))
    print("First 3 cards:", deck[:3])

.. code-block:: none

    Number of cards: 8
    First 3 cards: [Card("EXAMPL0", ['EDITED', 3.14, 'string', '', '', 0, 1, 2]), Card("EXAMPL1", [101, 'EDITED', 'string', '', '', 0, 1, 2]), Card("EXAMPL2", [101, 3.14, 'EDITED', '', '', 0, 1, 2])]

The :meth:`~bulkdata.deck.Deck.dumps` method returns the deck's
string representation, which is the concatenation of its cards'
string representations.

Just like the :class:`~bulkdata.card.Card` class, printing the
:class:`~bulkdata.deck.Deck` object uses the
:meth:`~bulkdata.deck.Deck.dumps` method,
which defaults to *fixed* format if no format argument is provided.

.. code-block:: python

    # these are all analogous

    # print(deck.dumps("fixed"))
    # print(deck.dumps())
    print(deck)

.. code-block:: none

    EXAMPL0 EDITED  3.14    string                  0       1       2
    EXAMPL1 101     EDITED  string                  0       1       2
    EXAMPL2 101     3.14    EDITED                  0       1       2
    EXAMPL3 101     3.14    string  EDITED          0       1       2
    EXAMPL4 101     3.14    string          EDITED  0       1       2
    EXAMPL5 101     3.14    string                  EDITED  1       2
    EXAMPL6 101     3.14    string                  0       EDITED  2
    EXAMPL7 101     3.14    string                  0       1       EDITED


And we can also specify the *free* format.

.. code-block:: python

    print(deck.dumps("free"))

.. code-block:: none

    EXAMPL0,EDITED,3.14,string, , ,0,1,2
    EXAMPL1,101,EDITED,string, , ,0,1,2
    EXAMPL2,101,3.14,EDITED, , ,0,1,2
    EXAMPL3,101,3.14,string,EDITED, ,0,1,2
    EXAMPL4,101,3.14,string, ,EDITED,0,1,2
    EXAMPL5,101,3.14,string, , ,EDITED,1,2
    EXAMPL6,101,3.14,string, , ,0,EDITED,2
    EXAMPL7,101,3.14,string, , ,0,1,EDITED


Load deck
^^^^^^^^^

The driving motivation for this package is to provide the ability
to load a BDF file, generated by some external program or process,
and update its contents with minimal effort. To do this,
we use the :meth:`~bulkdata.deck.Deck.load` classmethod to load
the contents of a file object into a
:class:`~bulkdata.deck.Deck` object.

.. code-block:: python

    # the "usage-example.bdf" file is adapted from the pyNastran "testA.bdf" file found here:
    # https://github.com/SteveDoyle2/pyNastran/blob/master/pyNastran/bdf/test/unit/testA.bdf
    #
    # please keep in mind that the original "testA.bdf" was created for testing purposes and
    # therefore contains some "rubbish" cards (as does "usage-example.bdf")
    bdf_filename = "usage-example.bdf"

    with open(bdf_filename) as bdf_file:
        deck = Deck.load(bdf_file)
        
    print("Number of cards:", len(deck))

.. code-block:: none

    Number of cards: 143

Update deck
^^^^^^^^^^^

The BDF file contains an AERO card. Let's find it.

.. code-block:: python

    # get all cards with name "AERO"
    aero_cards = list(deck.find({"name": "AERO"}))

    print("Number of AERO cards:", len(aero_cards))

    aero_card = aero_cards[0]

    print(aero_card.dumps("free"))

.. code-block:: none

    Number of AERO cards: 1
    AERO, , ,1.0,1.0

The :meth:`~bulkdata.deck.Deck.find` method returns a generator
object with all cards from the deck matching the *filter* argument,
in the above case ``{"name": "AERO"}``. The *name* keyword tells
the deck to filter for cards matching the specified name.
In this case, since we know we there is only once AERO card,
we can use the :meth:`~bulkdata.deck.Deck.find_one` method,
which returns the first matching card directly. 

Also, if we are only interested in filtering for the name,
we can pass the name string directly as the *filter* argument,
as a shortcut.

.. code-block:: python

    aero_card = deck.find_one("AERO")

The AERO card is defined in the **NASTRAN** manual as follows:

.. code-block:: none

    +------+-------+----------+------+--------+-------+-------+
    |   1  |   2   |    3     |   4  |   5    |   6   |   7   |
    +======+=======+==========+======+========+=======+=======+
    | AERO | ACSID | VELOCITY | REFC | RHOREF | SYMXZ | SYMXY |
    +------+-------+----------+------+--------+-------+-------+
    | AERO |   3   |   1.3+   | 100. |  1.-5  |   1   |  -1   |
    +------+-------+----------+------+--------+-------+-------+
 
From this we can see that the AERO card in the deck has blank
ACSID and VELOCITY entries; both REFC and RHOREF entries have
a value of 1.0; and SYMXZ, SYMXY entries are missing
(same as blank).

Let's update it to match the example from the manual.

.. code-block:: python

    # ACSID
    aero_card[0] = 3

    # VELOCITY
    aero_card[1] = 1.3

    # REFC
    aero_card[2] = 100.

    # RHOREF
    aero_card[3] = 1.0e-5

    # SYMXZ
    aero_card.append(1)

    # SYMXY
    aero_card.append(-1)

    # verify that it was updated in the deck
    print(deck.find_one("AERO"))

.. code-block:: none

    AERO    3       1.3     100.    .00001  1       -1


Alternatively, we can replace the card using the
:meth:`~bulkdata.deck.Deck.replace_one` method.

.. code-block:: python

    # new AERO card
    aero_new = Card("AERO")
    aero_new.extend([4, 3.1, 99., 1.0e+5, -1, 1])

    deck.replace_one("AERO", aero_new)

    # verify that it was updated in the deck
    print(deck.find_one("AERO"))

.. code-block:: none

    AERO    4       3.1     99.     100000. -1      1


In the case of AERO, there is only a single unique card.
But what if we want to update several matching cards?

The BDF file contains several GRID cards...

.. code-block:: python

    grid_cards = list(deck.find("GRID"))

    print("Number of GRID cards:", len(grid_cards))

.. code-block:: none

    Number of GRID cards: 43

... 43 to be exact. Let's increment each GRID card's
first field (NID entry) by 1.

.. code-block:: python

    print("NIDs before update:")
    for card in grid_cards:
        print(card[0], end=" ")
        # increment NID
        card[0] += 1
        
    print("\n\nNIDs after update:")
    for card in deck.find("GRID"):
        print(card[0], end=" ")

.. code-block:: none

    NIDs before update:
    1 4 40 41 50 60 120 121 200 1000 1003 1004 1005 1006 1008 1009 1010 1011 1012 2573 2574 2575 2576 16411 16412 16413 16414 16415 16416 16417 16418 16419 10006 10106 10206 10306 10406 10506 10606 10706 10806 12043 31201 

    NIDs after update:
    2 5 41 42 51 61 121 122 201 1001 1004 1005 1006 1007 1009 1010 1011 1012 1013 2574 2575 2576 2577 16412 16413 16414 16415 16416 16417 16418 16419 16420 10007 10107 10207 10307 10407 10507 10607 10707 10807 12044 31202 

More on filtering
^^^^^^^^^^^^^^^^^

Until this point, we have only filtered for a name,
but more complex filtering is also possible.

To find cards with specific field values, use the *fields* keyword:

.. code-block:: python

    filter_ = {
        # name is MAT1
        "name": "MAT1", 
        
        "fields": {
            
            # second field
            "index": 1,
            
            # with value 3.0e7
            "value": 3.0e7
        }
    }

    for card in deck.find(filter_):
        print(card, end="")

.. code-block:: none

    MAT1    765     3.+7
    MAT1    770     3.+7
    MAT1    795     3.+7
    MAT1    796     3.+7
    MAT1    769     3.+7
    MAT1    7       3.+7
    MAT1    8       3.+7
    MAT1    10      3.+7
    MAT1    200     3.+7
    MAT1    2       3.+7


To find cards containing a specific value (in any field),
use the *contains* keyword:

.. code-block:: python

    filter_ = {
        # any card containing the "THRU" field
        "contains": "THRU" 
    }

    for card in deck.find(filter_):
        print(card, end="")

.. code-block:: none

    PLOAD2  13      1.      2100001 THRU    2100003
    QBDY3   34      20.             1       THRU    7       BY      2       +0      
    +0      10      THRU    40      BY      5       42      45      THRU    +1      
    +1      48
    QBDY3   500     50000.0         10      THRU    60      BY      10
    PLOAD4  510     101     5.                              THRU    112
    DDVAL   10      0.1     0.5                                             +0      
    +0      1.0     THRU    100.    BY      1.0
    ASET1   3       1       THRU    8
    ASET1   3       10      THRU    16
    SESET   0       1       THRU    10

Combining the *name*, *fields*, and *contains* filter keywords:

.. code-block:: python

    filter_ = {
        # name is ASET1
        "name": "ASET1", 
        
        "fields": {
            
            # first field
            "index": 0,
            
            # with value 3
            "value": 3
        },
        
        # contains values 1 and "THRU"
        "contains": [1, "THRU"] 
    }

    for card in deck.find(filter_):
        print(card, end="")

.. code-block:: none

    ASET1   3       1       THRU    8

By the way, not providing a filter argument at all,
will return all cards in the deck.

.. code-block:: python

    print(len(list(deck.find())))

.. code-block:: none

    143

Delete cards
^^^^^^^^^^^^

The BDF file contains a "JUNK" card, let's remove it from the deck.

.. code-block:: python

    # delete all cards with name "JUNK"
    num_deleted = deck.delete("JUNK")

    print("Number of cards deleted:", num_deleted)

    # verify that all "JUNK" cards have been deleted
    no_junk = deck.find_one("JUNK") is None
    print(no_junk)

.. code-block:: none

    Number of cards deleted: 1
    True

Just as with the :meth:`~bulkdata.deck.Deck.find` method,
we could delete the entire deck if we (recklessly) failed to
pass a filter argument.
It shouldn't be necessary to demonstrate this...

Dump deck
^^^^^^^^^

When we're ready to write our new and improved deck to file,
we use the :meth:`~bulkdata.deck.Deck.dump` method.

.. code-block:: python

    with open("usage-example-updated.bdf", "w") as bdf_file:
        deck.dump(bdf_file)

Just as with the :meth:`~bulkdata.deck.Deck.dumps` method,
the output format of :meth:`~bulkdata.deck.Deck.dump` defaults
to *fixed* but the *free* format may also be specified.

.. code-block:: python

    with open("usage-example-updated-free.bdf", "w") as bdf_file:
        deck.dump(bdf_file, format="free")

For more information on the :class:`~bulkdata.deck.Deck` class,
check out the API documentation.
