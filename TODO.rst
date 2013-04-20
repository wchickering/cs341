####
TODO
####

* DONE 2013-04-20 (bill) program to build the inverted index

* DONE 2013-04-20 (bill) python module to read the index

    **Input:** itemid

    **Output:** list of raw query ids

* DONE 2013-04-20 (bill) filter data program

    **Input:** (JSON) raw Walmart data

    **Output:** (JSON) filtered Walmart data

* TODO (charles) similarity calculation python module

  + DONE 2013-04-16 implement intersection size, union size, and jaccard
    similarity
  + TODO implement more efficient jaccard similarity algorithm

* DONE 2013-04-20 (jamie) testGen program to generate test input

    **Input:** (JSON) filtered Walmart data

    **Output:** file with one line per query that consists of...

        * list of shown items
        * list of previously clicked items by the user
        * (optional) what ended up getting clicked

* DONE 2013-04-20 (charles) reRank program

    The reRank program takes in the output of the testGen and run the algorithm
    for reordering the shown itmes for a query based on a user's previously
    clicked items.

  + DONE 2013-04-16 write skeleton program
  + DONE 2013-04-20 verify sorting or reordered shown items
  + DONE 2013-04-20 write loadQuery function (need testGen output)

