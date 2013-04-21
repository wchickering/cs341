####
TODO
####

* DONE 2013-04-20 program to build the inverted index

* DONE 2013-04-20 python module to read the index

    **Input:** itemid

    **Output:** list of raw query ids

* DONE 2013-04-20 filter data program

    **Input:** (JSON) raw Walmart data

    **Output:** (JSON) filtered Walmart data

* DONE 2013-04-20 similarity calculation python module

  + DONE 2013-04-16 implement intersection size, union size, and jaccard
    similarity
  + DONE 2013-04-20 implement more efficient jaccard similarity algorithm

* DONE 2013-04-20 testGen program to generate test input

    **Input:** (JSON) filtered Walmart data

    **Output:** file with one line per query that consists of...

        * list of shown items
        * list of previously clicked items by the user
        * (optional) what ended up getting clicked

* DONE 2013-04-20 reRank program

    The reRank program takes in the output of the testGen and run the algorithm
    for reordering the shown itmes for a query based on a user's previously
    clicked items.

  + DONE 2013-04-16 write skeleton program
  + DONE 2013-04-20 verify sorting or reordered shown items
  + DONE 2013-04-20 write loadQuery function (need testGen output)

* TODO Makefile

  + DONE 2013-04-20 write targets for building index, posting.dict, and
    filtering raw data
  + TODO write targets for reRank and evaluation programs


