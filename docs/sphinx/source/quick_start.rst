Quick-Start
=============

Be sure that you have *newground* installed.
Then create a logic program file *test.lp*:

.. code-block::
    
    a(1).
    a(2).
    b(1).

    #program rules.

    c(X) :- a(X), not b(X).

Note that the part above *#program rules* is grounded by traditional means,
whereas the part below is grounded via Body-decoupled Grounding.

With *test.lp* saved to disk you can use newground to create the rewritten program:

.. code-block:: console

    $ newground test.lp

The output should be:

.. code-block:: console

    $ newground test.lp
    a(1).
    a(2).
    b(1).
    r3_X(2) | r3_X(1).
    r3_X(2) :- sat.
    r3_X(1) :- sat.
    sat_r3 :- r3_X(2),c(2).
    sat_r3 :- r3_X(1),c(1).
    sat_r3 :- r3_X(2),not a(2).
    sat_r3 :- r3_X(1),not a(1).
    sat_r3 :- r3_X(2),b(2).
    sat_r3 :- r3_X(1),b(1).
    domain_rule_3_variable_X(2).
    domain_rule_3_variable_X(1).
    {c3(X) : domain_rule_3_variable_X(X)} .
    c(X) :- c3(X).
    r3_unfound(2) :- not a(2).
    r3_unfound(1) :- not a(1).
    r3_unfound(2) :- b(2).
    r3_unfound(1) :- b(1).
    :- not sat.
    sat :- sat_r3.
    :- c3(2), #sum{1,0 : r3_unfound(2)} >=1 .
    :- c3(1), #sum{1,0 : r3_unfound(1)} >=1 .
    dom(1).
    dom(2).
    #show a/1.
    #show b/1.
    #show c/1.

You can directly save the output to disk by e.g.:

.. code-block:: console

    $ newground test.lp > output.lp

By e.g. using clingo_ (or idlv_), you can convince yourself that the answer-sets are the same.
Note that the answer-sets are equal with respect to the intersection of the output of the BDG-reduction with the predicates of the original program.
To simulate this behavior we use the *--project* option, together with the *show* statements from the output.

.. code-block:: console

    $ clingo --project --model 0 output.lp
    clingo version 5.6.2
    Reading from output.lp
    Solving...
    Answer: 1
    a(1) a(2) b(1) c(2)
    SATISFIABLE

    Models       : 1
    Calls        : 1
    Time         : 0.001s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
    CPU Time     : 0.001s

When comparing to the original program be sure to **remove** the *#program rules.* line, by e.g., creating a copy of *test.lp* (*test_2.lp*) and removing the line there.
Then the outputs are the same.

.. code-block:: console
    
    $ clingo --project --model 0 test_2.lp 
    clingo version 5.6.2
    Reading from test_2.lp
    Solving...
    Answer: 1
    a(1) a(2) b(1) c(2)
    SATISFIABLE

    Models       : 1
    Calls        : 1
    Time         : 0.000s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
    CPU Time     : 0.000s

.. _clingo: https://potassco.org/clingo/
.. _idlv: https://github.com/DeMaCS-UNICAL/I-DLV#i-dlv--the-new-intelligent-grounder-of-dlv
 