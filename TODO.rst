####
TODO
####

* TODO make todo list

  + TODO example sub todo in progress

    - DONE 2013-04-16 example sub sub todo finished

* TODO (bill) program to build the inverted index

* TODO (bill) python module to read the index

    **Input:** itemid

    **Output:** list of raw query ids

* TODO (bill) filter data program

    **Input:** (JSON) raw Walmart data

    **Output:** (JSON) filtered Walmart data

* DONE 2013-04-16 (charles) similarity calculation python module

  + DONE 2013-04-16 implement intersection size, union size, and jaccard
    similarity

* TODO (jamie) testGen program to generate test input

    **Input:** (JSON) filtered Walmart data

    **Output:** file with one line per query that consists of...

        * list of shown items
        * list of previously clicked items by the user
        * (optional) what ended up getting clicked

* TODO (charles) reRank program

    The reRank program takes in the output of the testGen and run the algorithm
    for reordering the shown itmes for a query based on a user's previously
    clicked items.

  + DONE 2013-04-16 write skeleton program
  + TODO verify sorting or reordered shown items
  + TODO write loadQuery function (need testGen output)

