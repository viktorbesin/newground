Regression Tests
================

The regression tests of newground cover aggregate-rewritings, standard ASP programs and non-tight programs.
The tests are located in the *regression_tests* folder, where the aggregate-rewriting-tests are located in *regression_tests/aggregate_tests*,
and the ASP/non-tight tests are located in *regression_tests/newground_tests*.
At the time of writing (2023-10) the number of regression tests totals over 100.

What is actually tested?
--------------------------

Intuitively the tests check for equivalence.
But this is always delicate to define in the ASP context, 
due to different notions of equality (strong, etc.).
Therefore, this kind of equality *only* refers to a weak kind of equality,
where the following is ensured:

If Pi is a program, then R(Pi) is its rewritten program.
A solver generates A(Pi) many answer sets.
The set of answer sets from the rewritten program is A(R(Pi)), which is a set and where each answer set is wrt. intersection to the set of predicates from the ''original'' program.

It is then checked, that each answer set q in A(Pi), has an equvalent in A(R(Pi)), and vice versa.
Equivalence meaning here, that the answer sets exactly match.

What tests have been written?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In general we wrote tests of two kinds: Those that check our aggregate-rewritings and those that check our reduction.
Note that the tests capture various aspects of ASP, and were crafted iteratively.
Note that the tests 114 (S3-T4), 115 (S3-T4), 116 (S4-T4), 117 (S1), 118 (S1), 119 (S2), 120 (S2), check the experiments.

Setup
--------

In order to be able to test the regression tests, you need to be able to execute clingo from the command line (depending on your OS this might differ how to do this).
In more detail, the ``subprocess.Popen`` class is used, where clingo is passed as an argument.

Regression test script Synopsis
-----------------------------------

A script is provided to execute regression tests (*start_regression_tests.py*).
Synopsis of the script:

.. code-block:: console

    $ python start_regression_tests.py --help
    usage: Regression test for Answerset Equivalence Checker [-h]
                                                             [--mode {aggregates-rs-star,aggregates-rs-plus,aggregates-rs,aggregates-ra,aggregates-recursive,rewriting-tight,rewriting-shared-cycle,rewriting-level-mappings-1,rewriting-level-mappings-2,fully-grounded-tight,fully-grounded-shared-cycle,fully-grounded-level-mappings-1,fully-grounded-level-mappings-2,test-all}]
                                                             [--folder FOLDER]

    Checks equivalence of answersets produced by newground and clingo on all instance-
    encoding pairs in a subfolder.

    options:
      -h, --help            show this help message and exit
      --mode {aggregates-rs-star,aggregates-rs-plus,aggregates-rs,aggregates-ra,aggregates-recursive,rewriting-tight,rewriting-shared-cycle,rewriting-level-mappings-1,rewriting-level-mappings-2,fully-grounded-tight,fully-grounded-shared-cycle,fully-grounded-level-mappings-1,fully-grounded-level-mappings-2,test-all}
      --folder FOLDER

Mode
^^^^^

The mode specifies which things are checked.
In general there is one mode for every aggregate. And for every partly/fully-mode, non-tight-strategy pair.
It totals 14 strategies and one *test-all* strategy.

Folder
^^^^^^^

One can specify a specific folder, if one wants to execute tests beside the ones located in the *regression_tests/aggregate_tests* and *regression_tests/newground_tests* folders.

Automatic Testing
------------------

As specified in the GitHub actions file,
for each push to dev or main/master all tests are executed and have to pass, s.t. a test is treated as passed.
