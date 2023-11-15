Going into more Depth
======================

Input Format
------------

The accepted ASP syntax of the prototype is a subset of clingos accepted syntax. 
At the moment, the following syntax is accepted in general:

- Normal ASP programs, where each literal is a predicate, and the terms only consist of variables and constants,
- with the addition of **comparison** literals, when operating over an integer domain,
- further, (non-recursive) **Aggregates**, and
- the **#program rules.** rule.

However it is important to note that **different** techniques exist, both for the normal (non-tight) ASP case, as the aggregate case.

Using the theoretical results that one can ground parts of a program by traditional means and parts by Body-decoupled Grounding (resulting in newground), 
one separates these two parts with the **#program rules.** rule in the newground prototype.
All rules which are placed *above* **#program rules.** are grounded by traditional means,
and all rules placed *below* **#program rules.** are grounded by Body-decoupled Grounding.

Note however that the combination of comparisons and non-tight ASP programs is in general **not** allowed, i.e., a statement like:

.. code-block::

    c(Z) :- a(X), b(Y), Z = X + 1, Z < Y.

is **not** allowed.
Additionally, when using aggregates, equality (=) as the aggregate relation, and a variable as the aggregate bounds, the variable has to be bound.
E.g., the following is **not** supported (for the RS, RS-STAR, and RS-PLUS techniques, for the other ones it is allowed):

.. code-block::

    c(Z) :- Z = #sum{X : p(X)}.

The above is **not** supported for the RS, RS-STAR and RS-PLUS techniques!

Synapsis
-----------

By entering enter, you are able to choose from a variety of options:

.. code-block:: console

    $ newground --help    
    usage: newground [files]

    positional arguments:
      files

    options:
      -h, --help            show this help message and exit
      --no-show             Do not print #show-statements to avoid compatibility issues.
      --mode {rewrite-aggregates-ground-partly,rewrite-aggregates-no-ground,rewrite-aggregates-ground-fully}
      --aggregate-strategy {RA,RS,RS-PLUS,RS-STAR,RECURSIVE}
      --cyclic-strategy {assume-tight,level-mappings,shared-cycle-body-predicates,level-mappings-AAAI}

Positional Arguments
^^^^^^^^^^^^^^^^^^^^^

Consists of the **files** (input-files) argument.
Other (optional) arguments are listed below in subsections.

Help
^^^^^

Shows the synapsis of the program.

No-Show
^^^^^^^^^

If specified, then no *#show* statements are generated, as they are not accepted by all grounders/solvers.

Aggregate-Strategy
^^^^^^^^^^^^^^^^^^^

Specifies the used aggregate-rewriting strategy, s.t. newground can be used in conjunction with aggregates.
The possible modes are:

1. (Default) *RA*: Performs a light rewriting, meaning that the aggregates are not fully rewritten, therefore, aggregates are still present in the output program, although their elements are replaced, s.t. their elements can be grounded by newground.
2. *RS*: The standard rewriting method that fully rewrites the aggregates. It facilitates results, which enable one to efficiently rewrite certain classes of aggregates.
3. *RS-PLUS*: In certain contexts, this method outperforms the *RS* method.
4. *RS-STAR*: A method primarily used to understand the *RS-PLUS* method, and is a hybrid between *RS* and *RS-PLUS*. 
5. *RECURSIVE*: Rewrites an aggregate into a strict order of elements, and then performs an aggregate function on them.

Cyclic-Strategy
^^^^^^^^^^^^^^^^^

Specifies the used method for handling non-tight programs. 
In general all methods (with the exception of *assume-tight*) analyze the program into a set of strongly-connected-components (SCCs),
and perform a certain method on each such SCC.
Note that one only needs to intervene, if the SCCs intersect with the part of the program that shall be grounded via newground.

1. (DEFAULT) *assume-tight*: Assumes a tight ASP program (does not work for non-tight ASP programs).
2. *shared-cycle-body-predicates*: Balances Body-decoupled Grounding and traditional grounding, if needed.
3. *level-mappings*: Explicitly encodes the order of derivation for an SCC. Full BDG method.
4. *level-mappings-AAAI*: Explicitly encodes the order of derivation, but uses an improved method for intersections in the traditionally-grounded part.

Mode
^^^^^

Defines the general mode of operation of the program.

1. (Default) *rewrite-aggregates-ground-partly*: Aggregates are rewritten, and the newground reduction is performed, although the reduction uses some improvements that are only possible, when not the whole output is grounded (therefore delegating some effort to a traditional grounder).
2. *rewrite-aggregates-no-ground*: Aggregates are rewritten, but no reduction is performed, i.e., not using newground.
3. *rewrite-aggregates-ground-fully*: Aggregates are rewritten, and additionally fully performs the reduction s.t. the output is a fully grounded program.


Examples
----------

Below we show some examples, of how to use the prototype with some output.

Aggregate no grounding
^^^^^^^^^^^^^^^^^^^^^^^^^

The following examples shows the case, when one wants to get the aggregate rewriting without grounding the program by BDG.
For demonstration purposes a program is shown with a single max aggregate, which is rewritten with the **RS** procedure.
Assume for that the input program (*aggregate_test.lp*):

.. code-block:: 

    p(1).
    p(2).
    p(5).
    p(8).
    p(10).
    p(12).
    p(14).
    p(20).
    p(21).
    p(22).
    p(23).

    #program rules.
    :- 14 <= #max{X1 : p(X1), p(X2), p(X3), p(X4), X1 < X2, X1 < X3, X1 < X4, X2 < X3, X2 < X4,  X3 < X4, X4 - X1 < 7}.

The program is rewritten with the prototype and the *RS* strategy (but not using the reduction):

.. code-block:: console

    $ newground aggregate_test.lp --mode rewrite-aggregates-no-ground --aggregate-strategy RS > output.lp


Then the (commented) output program (*output.lp*) is:

.. code-block::
    
    #show p/1.
    #show q/1.
    p(1).
    p(2).
    p(5).
    p(8).
    p(10).
    p(12).
    p(14).
    p(20).
    p(21).
    p(22).
    p(23).
    q(15).
    %[COMMENT]: Rewriting-Start:
    %[COMMENT]: The following two lines resemble the different elements.
    max_ag0_left(1) :-  body_max_ag0_0(Y), Y >= 14.
    max_ag0_left(1) :-  body_max_ag0_1(X1), X1 >= 14.
    %[COMMENT]: The following two lines resemble the individual element tuples.
    body_max_ag0_1(X1) :- p(X1),p(X2),p(X3),p(X4),X1 < X2,X1 < X3,X1 < X4,X2 < X3,X2 < X4,X3 < X4,(X4-X1) < 7.
    body_max_ag0_0(Y) :- q(Y).
    %[COMMENT]: The following line corresponds to the original aggregate-line.
    #false :- max_ag0_left(1).

When using clingo, we get the expected output:

.. code-block:: console

    $ clingo output.lp    
    clingo version 5.6.2
    Reading from output.lp
    Solving...
    UNSATISFIABLE

    Models       : 0
    Calls        : 1
    Time         : 0.000s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
    CPU Time     : 0.000s


Normal Program shared-cycle-body-predicates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following example shows how the *shared-cycle-body-predicates* strategy behaves for non-tight programs.

For this we assume the following input program (*non_tight_test.lp*):

.. code-block:: 

    d(1).
    c(1,2).
    c(X,Y) :- a(X,Y).
    c(X,X) :- d(X).

    #program rules.
    a(X,Y) :- c(Y,X).

We use the *shared-cycle-body-predicates* strategy with the partly-grounded mode to ground this program:

.. code-block:: console

    $ newground --cyclic-strategy shared-cycle-body-predicates --mode rewrite-aggregates-ground-partly non_tight_test.lp > output.lp 

The contents of the (commented) *output.lp* file are the following:

.. code-block::

    d(1).
    c(1,2).
    c(X,Y) :- a(X,Y).
    c(X,X) :- d(X).

    %[COMMENT]: SAT checks for R4 (a(X,Y) :- c(Y,X))
    r4_X(1) | r4_X(2).
    r4_X(1) :- sat.
    r4_X(2) :- sat.
    r4_Y(1) | r4_Y(2).
    r4_Y(1) :- sat.
    r4_Y(2) :- sat.
    sat_r4 :- r4_X(1),r4_Y(1),a(1,1).
    sat_r4 :- r4_X(1),r4_Y(2),a(1,2).
    sat_r4 :- r4_X(2),r4_Y(1),a(2,1).
    sat_r4 :- r4_Y(2),r4_X(2),a(2,2).
    sat_r4 :- r4_X(1),r4_Y(1),not c(1,1).
    sat_r4 :- r4_X(2),r4_Y(1),not c(1,2).
    sat_r4 :- r4_X(1),r4_Y(2),not c(2,1).
    sat_r4 :- r4_Y(2),r4_X(2),not c(2,2).

    domain_rule_4_variable_X(1).
    domain_rule_4_variable_X(2).
    domain_rule_4_variable_Y(1).
    domain_rule_4_variable_Y(2).

    %[COMMENT]: Speciality of this rewriting-strategy, as c(Y,X) is in the body.
    %[COMMENT]: The naming of a4 (from a) is due to encapsulation of local effects.
    %[COMMENT]: Guessing the head.
    {a4(X,Y) : domain_rule_4_variable_X(X),domain_rule_4_variable_Y(Y)}  :- c(Y,X).
    %[COMMENT]: Whenever ''a4'' holds, ''a'' has to hold as well (encapsulation rules).
    a(X,Y) :- a4(X,Y).
    %[COMMENT]: Further encode (un)foundedness
    r4_unfound(1,1) :- not c(1,1).
    r4_unfound(2,1) :- not c(1,2).
    r4_unfound(1,2) :- not c(2,1).
    r4_unfound(2,2) :- not c(2,2).

    %[COMMENT]: Global rules for SAT and (un)foundedness.
    :- not sat.
    sat :- sat_r4.
    :- a4(1,1), #sum{1,0 : r4_unfound(1,1)} >=1 .
    :- a4(2,1), #sum{1,0 : r4_unfound(2,1)} >=1 .
    :- a4(1,2), #sum{1,0 : r4_unfound(1,2)} >=1 .
    :- a4(2,2), #sum{1,0 : r4_unfound(2,2)} >=1 .

    %[COMMENT]: Generic domain + show statements.
    dom(1).
    dom(2).
    #show d/1.
    #show c/2.
    #show a/2.


Next we compare the output of *output.lp* with the original output, which holds.
Note the *--project* option for clingo,
which is due to the fact that the answer-sets produced by newground equal
the answer sets of traditional grounding only with intersection to the original predicates.
Finally, note that if you want to execute the *non_tight_test.lp* program, you have to **remove** the *#program rules.* rule!

.. code-block:: console

    $ clingo --project --model 0 output.lp 
    clingo version 5.6.2
    Reading from output.lp
    Solving...
    Answer: 1
    d(1) c(1,2) c(1,1) a(2,1) a(1,1) c(2,1) a(1,2)
    SATISFIABLE

    Models       : 1
    Calls        : 1
    Time         : 0.008s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
    CPU Time     : 0.001s
 
Normal Program Level-Mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Next we consider the difference from the *shared-cycle-body-predicates* to the *level-mappings*, where here we use the *level-mappings-AAAI* strategy,
on the same input program as the program above (*shared-cycle-body-predicates*).

.. code-block:: 
    
    d(1).
    c(1,2).
    c(X,Y) :- a(X,Y).
    c(X,X) :- d(X).

    #program rules.
    a(X,Y) :- c(Y,X).

We use the *level-mappings-AAAI* strategy with the fully-grounded mode to ground this program:

.. code-block:: console

    $ newground --cyclic-strategy level-mappings-AAAI --mode rewrite-aggregates-ground-fully non_tight_test.lp > output.lp 

The contents of the (commented) *output.lp* file are the following:

.. code-block:: console

    d(1).
    c(1,2).
    %[COMMENT]: Speciality of this method
    %[COMMENT]: Note that this block is from above the #program rules. block and therefore grounded by traditional means,
    %[COMMENT]: but for this method it is required to rewrite rules in SCCs.
    c(X,Y) :- a(X,Y),prec(a(X,Y),c(X,Y)).
    :- a(X,Y), not c(X,Y).
    c(X,X) :- d(X).

    %[COMMENT]: Start of #program rules.
    r4_X(2) | r4_X(1).
    r4_X(2) :- sat.
    r4_X(1) :- sat.
    r4_Y(1) | r4_Y(2).
    r4_Y(1) :- sat.
    r4_Y(2) :- sat.

    %[COMMENT]: SAT checks.
    sat_r4 :- r4_Y(1),r4_X(2),a(2,1).
    sat_r4 :- r4_Y(2),r4_X(2),a(2,2).
    sat_r4 :- r4_X(1),r4_Y(1),a(1,1).
    sat_r4 :- r4_Y(2),r4_X(1),a(1,2).
    sat_r4 :- r4_Y(1),r4_X(2),not c(1,2).
    sat_r4 :- r4_X(1),r4_Y(1),not c(1,1).
    sat_r4 :- r4_Y(2),r4_X(2),not c(2,2).
    sat_r4 :- r4_Y(2),r4_X(1),not c(2,1).
    %[COMMENT]: Encapsulation rules.
    a(2,1) :- a4(2,1).
    a(2,2) :- a4(2,2).
    a(1,1) :- a4(1,1).
    a(1,2) :- a4(1,2).

    %[COMMENT]: Guessing the head.
    {a4(2,1);a4(2,2);a4(1,1);a4(1,2)}.

    %[COMMENT]: (un)foudnedness checks.
    r4_unfound(2,1) :- not c(1,2).
    r4_unfound(2,1) :- not prec(c(1,2),a4(2,1)).
    r4_4_unfound(1,2) :- not prec(a4(2,1),a(2,1)).
    r4_unfound(1,1) :- not c(1,1).
    r4_unfound(1,1) :- not prec(c(1,1),a4(1,1)).
    r4_4_unfound(1,1) :- not prec(a4(1,1),a(1,1)).
    r4_unfound(2,2) :- not c(2,2).
    r4_unfound(2,2) :- not prec(c(2,2),a4(2,2)).
    r4_4_unfound(2,2) :- not prec(a4(2,2),a(2,2)).
    r4_unfound(1,2) :- not c(2,1).
    r4_unfound(1,2) :- not prec(c(2,1),a4(1,2)).
    r4_4_unfound(2,1) :- not prec(a4(1,2),a(1,2)).

    %[COMMENT]: Guessing derivation orders.
    1 <= {prec(a(2,1),a4(1,1));prec(a4(1,1),a(2,1))} <= 1.
    1 <= {prec(a(2,1),a4(1,2));prec(a4(1,2),a(2,1))} <= 1.
    1 <= {prec(a(2,1),a4(2,1));prec(a4(2,1),a(2,1))} <= 1.
    1 <= {prec(a(2,1),a4(2,2));prec(a4(2,2),a(2,1))} <= 1.
    1 <= {prec(a(2,2),a4(1,1));prec(a4(1,1),a(2,2))} <= 1.
    1 <= {prec(a(2,2),a4(1,2));prec(a4(1,2),a(2,2))} <= 1.
    1 <= {prec(a(2,2),a4(2,1));prec(a4(2,1),a(2,2))} <= 1.
    1 <= {prec(a(2,2),a4(2,2));prec(a4(2,2),a(2,2))} <= 1.
    1 <= {prec(a(1,1),a4(1,1));prec(a4(1,1),a(1,1))} <= 1.
    1 <= {prec(a(1,1),a4(1,2));prec(a4(1,2),a(1,1))} <= 1.
    1 <= {prec(a(1,1),a4(2,1));prec(a4(2,1),a(1,1))} <= 1.
    1 <= {prec(a(1,1),a4(2,2));prec(a4(2,2),a(1,1))} <= 1.
    1 <= {prec(a(1,2),a4(1,1));prec(a4(1,1),a(1,2))} <= 1.
    1 <= {prec(a(1,2),a4(1,2));prec(a4(1,2),a(1,2))} <= 1.
    1 <= {prec(a(1,2),a4(2,1));prec(a4(2,1),a(1,2))} <= 1.
    1 <= {prec(a(1,2),a4(2,2));prec(a4(2,2),a(1,2))} <= 1.
    1 <= {prec(a(2,1),c(1,2));prec(c(1,2),a(2,1))} <= 1.
    1 <= {prec(a(2,1),c(1,1));prec(c(1,1),a(2,1))} <= 1.
    1 <= {prec(a(2,1),c(2,2));prec(c(2,2),a(2,1))} <= 1.
    1 <= {prec(a(2,1),c(2,1));prec(c(2,1),a(2,1))} <= 1.
    1 <= {prec(a(2,2),c(1,2));prec(c(1,2),a(2,2))} <= 1.
    1 <= {prec(a(2,2),c(1,1));prec(c(1,1),a(2,2))} <= 1.
    1 <= {prec(a(2,2),c(2,2));prec(c(2,2),a(2,2))} <= 1.
    1 <= {prec(a(2,2),c(2,1));prec(c(2,1),a(2,2))} <= 1.
    1 <= {prec(a(1,1),c(1,2));prec(c(1,2),a(1,1))} <= 1.
    1 <= {prec(a(1,1),c(1,1));prec(c(1,1),a(1,1))} <= 1.
    1 <= {prec(a(1,1),c(2,2));prec(c(2,2),a(1,1))} <= 1.
    1 <= {prec(a(1,1),c(2,1));prec(c(2,1),a(1,1))} <= 1.
    1 <= {prec(a(1,2),c(1,2));prec(c(1,2),a(1,2))} <= 1.
    1 <= {prec(a(1,2),c(1,1));prec(c(1,1),a(1,2))} <= 1.
    1 <= {prec(a(1,2),c(2,2));prec(c(2,2),a(1,2))} <= 1.
    1 <= {prec(a(1,2),c(2,1));prec(c(2,1),a(1,2))} <= 1.
    1 <= {prec(a4(1,1),c(1,2));prec(c(1,2),a4(1,1))} <= 1.
    1 <= {prec(a4(1,1),c(1,1));prec(c(1,1),a4(1,1))} <= 1.
    1 <= {prec(a4(1,1),c(2,2));prec(c(2,2),a4(1,1))} <= 1.
    1 <= {prec(a4(1,1),c(2,1));prec(c(2,1),a4(1,1))} <= 1.
    1 <= {prec(a4(1,2),c(1,2));prec(c(1,2),a4(1,2))} <= 1.
    1 <= {prec(a4(1,2),c(1,1));prec(c(1,1),a4(1,2))} <= 1.
    1 <= {prec(a4(1,2),c(2,2));prec(c(2,2),a4(1,2))} <= 1.
    1 <= {prec(a4(1,2),c(2,1));prec(c(2,1),a4(1,2))} <= 1.
    1 <= {prec(a4(2,1),c(1,2));prec(c(1,2),a4(2,1))} <= 1.
    1 <= {prec(a4(2,1),c(1,1));prec(c(1,1),a4(2,1))} <= 1.
    1 <= {prec(a4(2,1),c(2,2));prec(c(2,2),a4(2,1))} <= 1.
    1 <= {prec(a4(2,1),c(2,1));prec(c(2,1),a4(2,1))} <= 1.
    1 <= {prec(a4(2,2),c(1,2));prec(c(1,2),a4(2,2))} <= 1.
    1 <= {prec(a4(2,2),c(1,1));prec(c(1,1),a4(2,2))} <= 1.
    1 <= {prec(a4(2,2),c(2,2));prec(c(2,2),a4(2,2))} <= 1.
    1 <= {prec(a4(2,2),c(2,1));prec(c(2,1),a4(2,2))} <= 1.

    %[COMMENT]: Ensuring transitivity of derivation orders.
    :- prec(a(2,1),a4(1,1)), prec(a4(1,1),c(1,2)), prec(c(1,2),a(2,1)).
    :- prec(a(2,1),a4(1,1)), prec(a4(1,1),c(1,1)), prec(c(1,1),a(2,1)).
    :- prec(a(2,1),a4(1,1)), prec(a4(1,1),c(2,2)), prec(c(2,2),a(2,1)).
    :- prec(a(2,1),a4(1,1)), prec(a4(1,1),c(2,1)), prec(c(2,1),a(2,1)).
    :- prec(a(2,1),a4(1,2)), prec(a4(1,2),c(1,2)), prec(c(1,2),a(2,1)).
    :- prec(a(2,1),a4(1,2)), prec(a4(1,2),c(1,1)), prec(c(1,1),a(2,1)).
    :- prec(a(2,1),a4(1,2)), prec(a4(1,2),c(2,2)), prec(c(2,2),a(2,1)).
    :- prec(a(2,1),a4(1,2)), prec(a4(1,2),c(2,1)), prec(c(2,1),a(2,1)).
    :- prec(a(2,1),a4(2,1)), prec(a4(2,1),c(1,2)), prec(c(1,2),a(2,1)).
    :- prec(a(2,1),a4(2,1)), prec(a4(2,1),c(1,1)), prec(c(1,1),a(2,1)).
    :- prec(a(2,1),a4(2,1)), prec(a4(2,1),c(2,2)), prec(c(2,2),a(2,1)).
    :- prec(a(2,1),a4(2,1)), prec(a4(2,1),c(2,1)), prec(c(2,1),a(2,1)).
    :- prec(a(2,1),a4(2,2)), prec(a4(2,2),c(1,2)), prec(c(1,2),a(2,1)).
    :- prec(a(2,1),a4(2,2)), prec(a4(2,2),c(1,1)), prec(c(1,1),a(2,1)).
    :- prec(a(2,1),a4(2,2)), prec(a4(2,2),c(2,2)), prec(c(2,2),a(2,1)).
    :- prec(a(2,1),a4(2,2)), prec(a4(2,2),c(2,1)), prec(c(2,1),a(2,1)).
    :- prec(a(2,2),a4(1,1)), prec(a4(1,1),c(1,2)), prec(c(1,2),a(2,2)).
    :- prec(a(2,2),a4(1,1)), prec(a4(1,1),c(1,1)), prec(c(1,1),a(2,2)).
    :- prec(a(2,2),a4(1,1)), prec(a4(1,1),c(2,2)), prec(c(2,2),a(2,2)).
    :- prec(a(2,2),a4(1,1)), prec(a4(1,1),c(2,1)), prec(c(2,1),a(2,2)).
    :- prec(a(2,2),a4(1,2)), prec(a4(1,2),c(1,2)), prec(c(1,2),a(2,2)).
    :- prec(a(2,2),a4(1,2)), prec(a4(1,2),c(1,1)), prec(c(1,1),a(2,2)).
    :- prec(a(2,2),a4(1,2)), prec(a4(1,2),c(2,2)), prec(c(2,2),a(2,2)).
    :- prec(a(2,2),a4(1,2)), prec(a4(1,2),c(2,1)), prec(c(2,1),a(2,2)).
    :- prec(a(2,2),a4(2,1)), prec(a4(2,1),c(1,2)), prec(c(1,2),a(2,2)).
    :- prec(a(2,2),a4(2,1)), prec(a4(2,1),c(1,1)), prec(c(1,1),a(2,2)).
    :- prec(a(2,2),a4(2,1)), prec(a4(2,1),c(2,2)), prec(c(2,2),a(2,2)).
    :- prec(a(2,2),a4(2,1)), prec(a4(2,1),c(2,1)), prec(c(2,1),a(2,2)).
    :- prec(a(2,2),a4(2,2)), prec(a4(2,2),c(1,2)), prec(c(1,2),a(2,2)).
    :- prec(a(2,2),a4(2,2)), prec(a4(2,2),c(1,1)), prec(c(1,1),a(2,2)).
    :- prec(a(2,2),a4(2,2)), prec(a4(2,2),c(2,2)), prec(c(2,2),a(2,2)).
    :- prec(a(2,2),a4(2,2)), prec(a4(2,2),c(2,1)), prec(c(2,1),a(2,2)).
    :- prec(a(1,1),a4(1,1)), prec(a4(1,1),c(1,2)), prec(c(1,2),a(1,1)).
    :- prec(a(1,1),a4(1,1)), prec(a4(1,1),c(1,1)), prec(c(1,1),a(1,1)).
    :- prec(a(1,1),a4(1,1)), prec(a4(1,1),c(2,2)), prec(c(2,2),a(1,1)).
    :- prec(a(1,1),a4(1,1)), prec(a4(1,1),c(2,1)), prec(c(2,1),a(1,1)).
    :- prec(a(1,1),a4(1,2)), prec(a4(1,2),c(1,2)), prec(c(1,2),a(1,1)).
    :- prec(a(1,1),a4(1,2)), prec(a4(1,2),c(1,1)), prec(c(1,1),a(1,1)).
    :- prec(a(1,1),a4(1,2)), prec(a4(1,2),c(2,2)), prec(c(2,2),a(1,1)).
    :- prec(a(1,1),a4(1,2)), prec(a4(1,2),c(2,1)), prec(c(2,1),a(1,1)).
    :- prec(a(1,1),a4(2,1)), prec(a4(2,1),c(1,2)), prec(c(1,2),a(1,1)).
    :- prec(a(1,1),a4(2,1)), prec(a4(2,1),c(1,1)), prec(c(1,1),a(1,1)).
    :- prec(a(1,1),a4(2,1)), prec(a4(2,1),c(2,2)), prec(c(2,2),a(1,1)).
    :- prec(a(1,1),a4(2,1)), prec(a4(2,1),c(2,1)), prec(c(2,1),a(1,1)).
    :- prec(a(1,1),a4(2,2)), prec(a4(2,2),c(1,2)), prec(c(1,2),a(1,1)).
    :- prec(a(1,1),a4(2,2)), prec(a4(2,2),c(1,1)), prec(c(1,1),a(1,1)).
    :- prec(a(1,1),a4(2,2)), prec(a4(2,2),c(2,2)), prec(c(2,2),a(1,1)).
    :- prec(a(1,1),a4(2,2)), prec(a4(2,2),c(2,1)), prec(c(2,1),a(1,1)).
    :- prec(a(1,2),a4(1,1)), prec(a4(1,1),c(1,2)), prec(c(1,2),a(1,2)).
    :- prec(a(1,2),a4(1,1)), prec(a4(1,1),c(1,1)), prec(c(1,1),a(1,2)).
    :- prec(a(1,2),a4(1,1)), prec(a4(1,1),c(2,2)), prec(c(2,2),a(1,2)).
    :- prec(a(1,2),a4(1,1)), prec(a4(1,1),c(2,1)), prec(c(2,1),a(1,2)).
    :- prec(a(1,2),a4(1,2)), prec(a4(1,2),c(1,2)), prec(c(1,2),a(1,2)).
    :- prec(a(1,2),a4(1,2)), prec(a4(1,2),c(1,1)), prec(c(1,1),a(1,2)).
    :- prec(a(1,2),a4(1,2)), prec(a4(1,2),c(2,2)), prec(c(2,2),a(1,2)).
    :- prec(a(1,2),a4(1,2)), prec(a4(1,2),c(2,1)), prec(c(2,1),a(1,2)).
    :- prec(a(1,2),a4(2,1)), prec(a4(2,1),c(1,2)), prec(c(1,2),a(1,2)).
    :- prec(a(1,2),a4(2,1)), prec(a4(2,1),c(1,1)), prec(c(1,1),a(1,2)).
    :- prec(a(1,2),a4(2,1)), prec(a4(2,1),c(2,2)), prec(c(2,2),a(1,2)).
    :- prec(a(1,2),a4(2,1)), prec(a4(2,1),c(2,1)), prec(c(2,1),a(1,2)).
    :- prec(a(1,2),a4(2,2)), prec(a4(2,2),c(1,2)), prec(c(1,2),a(1,2)).
    :- prec(a(1,2),a4(2,2)), prec(a4(2,2),c(1,1)), prec(c(1,1),a(1,2)).
    :- prec(a(1,2),a4(2,2)), prec(a4(2,2),c(2,2)), prec(c(2,2),a(1,2)).
    :- prec(a(1,2),a4(2,2)), prec(a4(2,2),c(2,1)), prec(c(2,1),a(1,2)).
    :- prec(a(2,1),c(1,2)), prec(c(1,2),a4(1,1)), prec(a4(1,1),a(2,1)).
    :- prec(a(2,1),c(1,2)), prec(c(1,2),a4(1,2)), prec(a4(1,2),a(2,1)).
    :- prec(a(2,1),c(1,2)), prec(c(1,2),a4(2,1)), prec(a4(2,1),a(2,1)).
    :- prec(a(2,1),c(1,2)), prec(c(1,2),a4(2,2)), prec(a4(2,2),a(2,1)).
    :- prec(a(2,1),c(1,1)), prec(c(1,1),a4(1,1)), prec(a4(1,1),a(2,1)).
    :- prec(a(2,1),c(1,1)), prec(c(1,1),a4(1,2)), prec(a4(1,2),a(2,1)).
    :- prec(a(2,1),c(1,1)), prec(c(1,1),a4(2,1)), prec(a4(2,1),a(2,1)).
    :- prec(a(2,1),c(1,1)), prec(c(1,1),a4(2,2)), prec(a4(2,2),a(2,1)).
    :- prec(a(2,1),c(2,2)), prec(c(2,2),a4(1,1)), prec(a4(1,1),a(2,1)).
    :- prec(a(2,1),c(2,2)), prec(c(2,2),a4(1,2)), prec(a4(1,2),a(2,1)).
    :- prec(a(2,1),c(2,2)), prec(c(2,2),a4(2,1)), prec(a4(2,1),a(2,1)).
    :- prec(a(2,1),c(2,2)), prec(c(2,2),a4(2,2)), prec(a4(2,2),a(2,1)).
    :- prec(a(2,1),c(2,1)), prec(c(2,1),a4(1,1)), prec(a4(1,1),a(2,1)).
    :- prec(a(2,1),c(2,1)), prec(c(2,1),a4(1,2)), prec(a4(1,2),a(2,1)).
    :- prec(a(2,1),c(2,1)), prec(c(2,1),a4(2,1)), prec(a4(2,1),a(2,1)).
    :- prec(a(2,1),c(2,1)), prec(c(2,1),a4(2,2)), prec(a4(2,2),a(2,1)).
    :- prec(a(2,2),c(1,2)), prec(c(1,2),a4(1,1)), prec(a4(1,1),a(2,2)).
    :- prec(a(2,2),c(1,2)), prec(c(1,2),a4(1,2)), prec(a4(1,2),a(2,2)).
    :- prec(a(2,2),c(1,2)), prec(c(1,2),a4(2,1)), prec(a4(2,1),a(2,2)).
    :- prec(a(2,2),c(1,2)), prec(c(1,2),a4(2,2)), prec(a4(2,2),a(2,2)).
    :- prec(a(2,2),c(1,1)), prec(c(1,1),a4(1,1)), prec(a4(1,1),a(2,2)).
    :- prec(a(2,2),c(1,1)), prec(c(1,1),a4(1,2)), prec(a4(1,2),a(2,2)).
    :- prec(a(2,2),c(1,1)), prec(c(1,1),a4(2,1)), prec(a4(2,1),a(2,2)).
    :- prec(a(2,2),c(1,1)), prec(c(1,1),a4(2,2)), prec(a4(2,2),a(2,2)).
    :- prec(a(2,2),c(2,2)), prec(c(2,2),a4(1,1)), prec(a4(1,1),a(2,2)).
    :- prec(a(2,2),c(2,2)), prec(c(2,2),a4(1,2)), prec(a4(1,2),a(2,2)).
    :- prec(a(2,2),c(2,2)), prec(c(2,2),a4(2,1)), prec(a4(2,1),a(2,2)).
    :- prec(a(2,2),c(2,2)), prec(c(2,2),a4(2,2)), prec(a4(2,2),a(2,2)).
    :- prec(a(2,2),c(2,1)), prec(c(2,1),a4(1,1)), prec(a4(1,1),a(2,2)).
    :- prec(a(2,2),c(2,1)), prec(c(2,1),a4(1,2)), prec(a4(1,2),a(2,2)).
    :- prec(a(2,2),c(2,1)), prec(c(2,1),a4(2,1)), prec(a4(2,1),a(2,2)).
    :- prec(a(2,2),c(2,1)), prec(c(2,1),a4(2,2)), prec(a4(2,2),a(2,2)).
    :- prec(a(1,1),c(1,2)), prec(c(1,2),a4(1,1)), prec(a4(1,1),a(1,1)).
    :- prec(a(1,1),c(1,2)), prec(c(1,2),a4(1,2)), prec(a4(1,2),a(1,1)).
    :- prec(a(1,1),c(1,2)), prec(c(1,2),a4(2,1)), prec(a4(2,1),a(1,1)).
    :- prec(a(1,1),c(1,2)), prec(c(1,2),a4(2,2)), prec(a4(2,2),a(1,1)).
    :- prec(a(1,1),c(1,1)), prec(c(1,1),a4(1,1)), prec(a4(1,1),a(1,1)).
    :- prec(a(1,1),c(1,1)), prec(c(1,1),a4(1,2)), prec(a4(1,2),a(1,1)).
    :- prec(a(1,1),c(1,1)), prec(c(1,1),a4(2,1)), prec(a4(2,1),a(1,1)).
    :- prec(a(1,1),c(1,1)), prec(c(1,1),a4(2,2)), prec(a4(2,2),a(1,1)).
    :- prec(a(1,1),c(2,2)), prec(c(2,2),a4(1,1)), prec(a4(1,1),a(1,1)).
    :- prec(a(1,1),c(2,2)), prec(c(2,2),a4(1,2)), prec(a4(1,2),a(1,1)).
    :- prec(a(1,1),c(2,2)), prec(c(2,2),a4(2,1)), prec(a4(2,1),a(1,1)).
    :- prec(a(1,1),c(2,2)), prec(c(2,2),a4(2,2)), prec(a4(2,2),a(1,1)).
    :- prec(a(1,1),c(2,1)), prec(c(2,1),a4(1,1)), prec(a4(1,1),a(1,1)).
    :- prec(a(1,1),c(2,1)), prec(c(2,1),a4(1,2)), prec(a4(1,2),a(1,1)).
    :- prec(a(1,1),c(2,1)), prec(c(2,1),a4(2,1)), prec(a4(2,1),a(1,1)).
    :- prec(a(1,1),c(2,1)), prec(c(2,1),a4(2,2)), prec(a4(2,2),a(1,1)).
    :- prec(a(1,2),c(1,2)), prec(c(1,2),a4(1,1)), prec(a4(1,1),a(1,2)).
    :- prec(a(1,2),c(1,2)), prec(c(1,2),a4(1,2)), prec(a4(1,2),a(1,2)).
    :- prec(a(1,2),c(1,2)), prec(c(1,2),a4(2,1)), prec(a4(2,1),a(1,2)).
    :- prec(a(1,2),c(1,2)), prec(c(1,2),a4(2,2)), prec(a4(2,2),a(1,2)).
    :- prec(a(1,2),c(1,1)), prec(c(1,1),a4(1,1)), prec(a4(1,1),a(1,2)).
    :- prec(a(1,2),c(1,1)), prec(c(1,1),a4(1,2)), prec(a4(1,2),a(1,2)).
    :- prec(a(1,2),c(1,1)), prec(c(1,1),a4(2,1)), prec(a4(2,1),a(1,2)).
    :- prec(a(1,2),c(1,1)), prec(c(1,1),a4(2,2)), prec(a4(2,2),a(1,2)).
    :- prec(a(1,2),c(2,2)), prec(c(2,2),a4(1,1)), prec(a4(1,1),a(1,2)).
    :- prec(a(1,2),c(2,2)), prec(c(2,2),a4(1,2)), prec(a4(1,2),a(1,2)).
    :- prec(a(1,2),c(2,2)), prec(c(2,2),a4(2,1)), prec(a4(2,1),a(1,2)).
    :- prec(a(1,2),c(2,2)), prec(c(2,2),a4(2,2)), prec(a4(2,2),a(1,2)).
    :- prec(a(1,2),c(2,1)), prec(c(2,1),a4(1,1)), prec(a4(1,1),a(1,2)).
    :- prec(a(1,2),c(2,1)), prec(c(2,1),a4(1,2)), prec(a4(1,2),a(1,2)).
    :- prec(a(1,2),c(2,1)), prec(c(2,1),a4(2,1)), prec(a4(2,1),a(1,2)).
    :- prec(a(1,2),c(2,1)), prec(c(2,1),a4(2,2)), prec(a4(2,2),a(1,2)).
    :- prec(a4(1,1),a(2,1)), prec(a(2,1),c(1,2)), prec(c(1,2),a4(1,1)).
    :- prec(a4(1,1),a(2,1)), prec(a(2,1),c(1,1)), prec(c(1,1),a4(1,1)).
    :- prec(a4(1,1),a(2,1)), prec(a(2,1),c(2,2)), prec(c(2,2),a4(1,1)).
    :- prec(a4(1,1),a(2,1)), prec(a(2,1),c(2,1)), prec(c(2,1),a4(1,1)).
    :- prec(a4(1,1),a(2,2)), prec(a(2,2),c(1,2)), prec(c(1,2),a4(1,1)).
    :- prec(a4(1,1),a(2,2)), prec(a(2,2),c(1,1)), prec(c(1,1),a4(1,1)).
    :- prec(a4(1,1),a(2,2)), prec(a(2,2),c(2,2)), prec(c(2,2),a4(1,1)).
    :- prec(a4(1,1),a(2,2)), prec(a(2,2),c(2,1)), prec(c(2,1),a4(1,1)).
    :- prec(a4(1,1),a(1,1)), prec(a(1,1),c(1,2)), prec(c(1,2),a4(1,1)).
    :- prec(a4(1,1),a(1,1)), prec(a(1,1),c(1,1)), prec(c(1,1),a4(1,1)).
    :- prec(a4(1,1),a(1,1)), prec(a(1,1),c(2,2)), prec(c(2,2),a4(1,1)).
    :- prec(a4(1,1),a(1,1)), prec(a(1,1),c(2,1)), prec(c(2,1),a4(1,1)).
    :- prec(a4(1,1),a(1,2)), prec(a(1,2),c(1,2)), prec(c(1,2),a4(1,1)).
    :- prec(a4(1,1),a(1,2)), prec(a(1,2),c(1,1)), prec(c(1,1),a4(1,1)).
    :- prec(a4(1,1),a(1,2)), prec(a(1,2),c(2,2)), prec(c(2,2),a4(1,1)).
    :- prec(a4(1,1),a(1,2)), prec(a(1,2),c(2,1)), prec(c(2,1),a4(1,1)).
    :- prec(a4(1,2),a(2,1)), prec(a(2,1),c(1,2)), prec(c(1,2),a4(1,2)).
    :- prec(a4(1,2),a(2,1)), prec(a(2,1),c(1,1)), prec(c(1,1),a4(1,2)).
    :- prec(a4(1,2),a(2,1)), prec(a(2,1),c(2,2)), prec(c(2,2),a4(1,2)).
    :- prec(a4(1,2),a(2,1)), prec(a(2,1),c(2,1)), prec(c(2,1),a4(1,2)).
    :- prec(a4(1,2),a(2,2)), prec(a(2,2),c(1,2)), prec(c(1,2),a4(1,2)).
    :- prec(a4(1,2),a(2,2)), prec(a(2,2),c(1,1)), prec(c(1,1),a4(1,2)).
    :- prec(a4(1,2),a(2,2)), prec(a(2,2),c(2,2)), prec(c(2,2),a4(1,2)).
    :- prec(a4(1,2),a(2,2)), prec(a(2,2),c(2,1)), prec(c(2,1),a4(1,2)).
    :- prec(a4(1,2),a(1,1)), prec(a(1,1),c(1,2)), prec(c(1,2),a4(1,2)).
    :- prec(a4(1,2),a(1,1)), prec(a(1,1),c(1,1)), prec(c(1,1),a4(1,2)).
    :- prec(a4(1,2),a(1,1)), prec(a(1,1),c(2,2)), prec(c(2,2),a4(1,2)).
    :- prec(a4(1,2),a(1,1)), prec(a(1,1),c(2,1)), prec(c(2,1),a4(1,2)).
    :- prec(a4(1,2),a(1,2)), prec(a(1,2),c(1,2)), prec(c(1,2),a4(1,2)).
    :- prec(a4(1,2),a(1,2)), prec(a(1,2),c(1,1)), prec(c(1,1),a4(1,2)).
    :- prec(a4(1,2),a(1,2)), prec(a(1,2),c(2,2)), prec(c(2,2),a4(1,2)).
    :- prec(a4(1,2),a(1,2)), prec(a(1,2),c(2,1)), prec(c(2,1),a4(1,2)).
    :- prec(a4(2,1),a(2,1)), prec(a(2,1),c(1,2)), prec(c(1,2),a4(2,1)).
    :- prec(a4(2,1),a(2,1)), prec(a(2,1),c(1,1)), prec(c(1,1),a4(2,1)).
    :- prec(a4(2,1),a(2,1)), prec(a(2,1),c(2,2)), prec(c(2,2),a4(2,1)).
    :- prec(a4(2,1),a(2,1)), prec(a(2,1),c(2,1)), prec(c(2,1),a4(2,1)).
    :- prec(a4(2,1),a(2,2)), prec(a(2,2),c(1,2)), prec(c(1,2),a4(2,1)).
    :- prec(a4(2,1),a(2,2)), prec(a(2,2),c(1,1)), prec(c(1,1),a4(2,1)).
    :- prec(a4(2,1),a(2,2)), prec(a(2,2),c(2,2)), prec(c(2,2),a4(2,1)).
    :- prec(a4(2,1),a(2,2)), prec(a(2,2),c(2,1)), prec(c(2,1),a4(2,1)).
    :- prec(a4(2,1),a(1,1)), prec(a(1,1),c(1,2)), prec(c(1,2),a4(2,1)).
    :- prec(a4(2,1),a(1,1)), prec(a(1,1),c(1,1)), prec(c(1,1),a4(2,1)).
    :- prec(a4(2,1),a(1,1)), prec(a(1,1),c(2,2)), prec(c(2,2),a4(2,1)).
    :- prec(a4(2,1),a(1,1)), prec(a(1,1),c(2,1)), prec(c(2,1),a4(2,1)).
    :- prec(a4(2,1),a(1,2)), prec(a(1,2),c(1,2)), prec(c(1,2),a4(2,1)).
    :- prec(a4(2,1),a(1,2)), prec(a(1,2),c(1,1)), prec(c(1,1),a4(2,1)).
    :- prec(a4(2,1),a(1,2)), prec(a(1,2),c(2,2)), prec(c(2,2),a4(2,1)).
    :- prec(a4(2,1),a(1,2)), prec(a(1,2),c(2,1)), prec(c(2,1),a4(2,1)).
    :- prec(a4(2,2),a(2,1)), prec(a(2,1),c(1,2)), prec(c(1,2),a4(2,2)).
    :- prec(a4(2,2),a(2,1)), prec(a(2,1),c(1,1)), prec(c(1,1),a4(2,2)).
    :- prec(a4(2,2),a(2,1)), prec(a(2,1),c(2,2)), prec(c(2,2),a4(2,2)).
    :- prec(a4(2,2),a(2,1)), prec(a(2,1),c(2,1)), prec(c(2,1),a4(2,2)).
    :- prec(a4(2,2),a(2,2)), prec(a(2,2),c(1,2)), prec(c(1,2),a4(2,2)).
    :- prec(a4(2,2),a(2,2)), prec(a(2,2),c(1,1)), prec(c(1,1),a4(2,2)).
    :- prec(a4(2,2),a(2,2)), prec(a(2,2),c(2,2)), prec(c(2,2),a4(2,2)).
    :- prec(a4(2,2),a(2,2)), prec(a(2,2),c(2,1)), prec(c(2,1),a4(2,2)).
    :- prec(a4(2,2),a(1,1)), prec(a(1,1),c(1,2)), prec(c(1,2),a4(2,2)).
    :- prec(a4(2,2),a(1,1)), prec(a(1,1),c(1,1)), prec(c(1,1),a4(2,2)).
    :- prec(a4(2,2),a(1,1)), prec(a(1,1),c(2,2)), prec(c(2,2),a4(2,2)).
    :- prec(a4(2,2),a(1,1)), prec(a(1,1),c(2,1)), prec(c(2,1),a4(2,2)).
    :- prec(a4(2,2),a(1,2)), prec(a(1,2),c(1,2)), prec(c(1,2),a4(2,2)).
    :- prec(a4(2,2),a(1,2)), prec(a(1,2),c(1,1)), prec(c(1,1),a4(2,2)).
    :- prec(a4(2,2),a(1,2)), prec(a(1,2),c(2,2)), prec(c(2,2),a4(2,2)).
    :- prec(a4(2,2),a(1,2)), prec(a(1,2),c(2,1)), prec(c(2,1),a4(2,2)).
    :- prec(a4(1,1),c(1,2)), prec(c(1,2),a(2,1)), prec(a(2,1),a4(1,1)).
    :- prec(a4(1,1),c(1,2)), prec(c(1,2),a(2,2)), prec(a(2,2),a4(1,1)).
    :- prec(a4(1,1),c(1,2)), prec(c(1,2),a(1,1)), prec(a(1,1),a4(1,1)).
    :- prec(a4(1,1),c(1,2)), prec(c(1,2),a(1,2)), prec(a(1,2),a4(1,1)).
    :- prec(a4(1,1),c(1,1)), prec(c(1,1),a(2,1)), prec(a(2,1),a4(1,1)).
    :- prec(a4(1,1),c(1,1)), prec(c(1,1),a(2,2)), prec(a(2,2),a4(1,1)).
    :- prec(a4(1,1),c(1,1)), prec(c(1,1),a(1,1)), prec(a(1,1),a4(1,1)).
    :- prec(a4(1,1),c(1,1)), prec(c(1,1),a(1,2)), prec(a(1,2),a4(1,1)).
    :- prec(a4(1,1),c(2,2)), prec(c(2,2),a(2,1)), prec(a(2,1),a4(1,1)).
    :- prec(a4(1,1),c(2,2)), prec(c(2,2),a(2,2)), prec(a(2,2),a4(1,1)).
    :- prec(a4(1,1),c(2,2)), prec(c(2,2),a(1,1)), prec(a(1,1),a4(1,1)).
    :- prec(a4(1,1),c(2,2)), prec(c(2,2),a(1,2)), prec(a(1,2),a4(1,1)).
    :- prec(a4(1,1),c(2,1)), prec(c(2,1),a(2,1)), prec(a(2,1),a4(1,1)).
    :- prec(a4(1,1),c(2,1)), prec(c(2,1),a(2,2)), prec(a(2,2),a4(1,1)).
    :- prec(a4(1,1),c(2,1)), prec(c(2,1),a(1,1)), prec(a(1,1),a4(1,1)).
    :- prec(a4(1,1),c(2,1)), prec(c(2,1),a(1,2)), prec(a(1,2),a4(1,1)).
    :- prec(a4(1,2),c(1,2)), prec(c(1,2),a(2,1)), prec(a(2,1),a4(1,2)).
    :- prec(a4(1,2),c(1,2)), prec(c(1,2),a(2,2)), prec(a(2,2),a4(1,2)).
    :- prec(a4(1,2),c(1,2)), prec(c(1,2),a(1,1)), prec(a(1,1),a4(1,2)).
    :- prec(a4(1,2),c(1,2)), prec(c(1,2),a(1,2)), prec(a(1,2),a4(1,2)).
    :- prec(a4(1,2),c(1,1)), prec(c(1,1),a(2,1)), prec(a(2,1),a4(1,2)).
    :- prec(a4(1,2),c(1,1)), prec(c(1,1),a(2,2)), prec(a(2,2),a4(1,2)).
    :- prec(a4(1,2),c(1,1)), prec(c(1,1),a(1,1)), prec(a(1,1),a4(1,2)).
    :- prec(a4(1,2),c(1,1)), prec(c(1,1),a(1,2)), prec(a(1,2),a4(1,2)).
    :- prec(a4(1,2),c(2,2)), prec(c(2,2),a(2,1)), prec(a(2,1),a4(1,2)).
    :- prec(a4(1,2),c(2,2)), prec(c(2,2),a(2,2)), prec(a(2,2),a4(1,2)).
    :- prec(a4(1,2),c(2,2)), prec(c(2,2),a(1,1)), prec(a(1,1),a4(1,2)).
    :- prec(a4(1,2),c(2,2)), prec(c(2,2),a(1,2)), prec(a(1,2),a4(1,2)).
    :- prec(a4(1,2),c(2,1)), prec(c(2,1),a(2,1)), prec(a(2,1),a4(1,2)).
    :- prec(a4(1,2),c(2,1)), prec(c(2,1),a(2,2)), prec(a(2,2),a4(1,2)).
    :- prec(a4(1,2),c(2,1)), prec(c(2,1),a(1,1)), prec(a(1,1),a4(1,2)).
    :- prec(a4(1,2),c(2,1)), prec(c(2,1),a(1,2)), prec(a(1,2),a4(1,2)).
    :- prec(a4(2,1),c(1,2)), prec(c(1,2),a(2,1)), prec(a(2,1),a4(2,1)).
    :- prec(a4(2,1),c(1,2)), prec(c(1,2),a(2,2)), prec(a(2,2),a4(2,1)).
    :- prec(a4(2,1),c(1,2)), prec(c(1,2),a(1,1)), prec(a(1,1),a4(2,1)).
    :- prec(a4(2,1),c(1,2)), prec(c(1,2),a(1,2)), prec(a(1,2),a4(2,1)).
    :- prec(a4(2,1),c(1,1)), prec(c(1,1),a(2,1)), prec(a(2,1),a4(2,1)).
    :- prec(a4(2,1),c(1,1)), prec(c(1,1),a(2,2)), prec(a(2,2),a4(2,1)).
    :- prec(a4(2,1),c(1,1)), prec(c(1,1),a(1,1)), prec(a(1,1),a4(2,1)).
    :- prec(a4(2,1),c(1,1)), prec(c(1,1),a(1,2)), prec(a(1,2),a4(2,1)).
    :- prec(a4(2,1),c(2,2)), prec(c(2,2),a(2,1)), prec(a(2,1),a4(2,1)).
    :- prec(a4(2,1),c(2,2)), prec(c(2,2),a(2,2)), prec(a(2,2),a4(2,1)).
    :- prec(a4(2,1),c(2,2)), prec(c(2,2),a(1,1)), prec(a(1,1),a4(2,1)).
    :- prec(a4(2,1),c(2,2)), prec(c(2,2),a(1,2)), prec(a(1,2),a4(2,1)).
    :- prec(a4(2,1),c(2,1)), prec(c(2,1),a(2,1)), prec(a(2,1),a4(2,1)).
    :- prec(a4(2,1),c(2,1)), prec(c(2,1),a(2,2)), prec(a(2,2),a4(2,1)).
    :- prec(a4(2,1),c(2,1)), prec(c(2,1),a(1,1)), prec(a(1,1),a4(2,1)).
    :- prec(a4(2,1),c(2,1)), prec(c(2,1),a(1,2)), prec(a(1,2),a4(2,1)).
    :- prec(a4(2,2),c(1,2)), prec(c(1,2),a(2,1)), prec(a(2,1),a4(2,2)).
    :- prec(a4(2,2),c(1,2)), prec(c(1,2),a(2,2)), prec(a(2,2),a4(2,2)).
    :- prec(a4(2,2),c(1,2)), prec(c(1,2),a(1,1)), prec(a(1,1),a4(2,2)).
    :- prec(a4(2,2),c(1,2)), prec(c(1,2),a(1,2)), prec(a(1,2),a4(2,2)).
    :- prec(a4(2,2),c(1,1)), prec(c(1,1),a(2,1)), prec(a(2,1),a4(2,2)).
    :- prec(a4(2,2),c(1,1)), prec(c(1,1),a(2,2)), prec(a(2,2),a4(2,2)).
    :- prec(a4(2,2),c(1,1)), prec(c(1,1),a(1,1)), prec(a(1,1),a4(2,2)).
    :- prec(a4(2,2),c(1,1)), prec(c(1,1),a(1,2)), prec(a(1,2),a4(2,2)).
    :- prec(a4(2,2),c(2,2)), prec(c(2,2),a(2,1)), prec(a(2,1),a4(2,2)).
    :- prec(a4(2,2),c(2,2)), prec(c(2,2),a(2,2)), prec(a(2,2),a4(2,2)).
    :- prec(a4(2,2),c(2,2)), prec(c(2,2),a(1,1)), prec(a(1,1),a4(2,2)).
    :- prec(a4(2,2),c(2,2)), prec(c(2,2),a(1,2)), prec(a(1,2),a4(2,2)).
    :- prec(a4(2,2),c(2,1)), prec(c(2,1),a(2,1)), prec(a(2,1),a4(2,2)).
    :- prec(a4(2,2),c(2,1)), prec(c(2,1),a(2,2)), prec(a(2,2),a4(2,2)).
    :- prec(a4(2,2),c(2,1)), prec(c(2,1),a(1,1)), prec(a(1,1),a4(2,2)).
    :- prec(a4(2,2),c(2,1)), prec(c(2,1),a(1,2)), prec(a(1,2),a4(2,2)).
    :- prec(c(1,2),a(2,1)), prec(a(2,1),a4(1,1)), prec(a4(1,1),c(1,2)).
    :- prec(c(1,2),a(2,1)), prec(a(2,1),a4(1,2)), prec(a4(1,2),c(1,2)).
    :- prec(c(1,2),a(2,1)), prec(a(2,1),a4(2,1)), prec(a4(2,1),c(1,2)).
    :- prec(c(1,2),a(2,1)), prec(a(2,1),a4(2,2)), prec(a4(2,2),c(1,2)).
    :- prec(c(1,2),a(2,2)), prec(a(2,2),a4(1,1)), prec(a4(1,1),c(1,2)).
    :- prec(c(1,2),a(2,2)), prec(a(2,2),a4(1,2)), prec(a4(1,2),c(1,2)).
    :- prec(c(1,2),a(2,2)), prec(a(2,2),a4(2,1)), prec(a4(2,1),c(1,2)).
    :- prec(c(1,2),a(2,2)), prec(a(2,2),a4(2,2)), prec(a4(2,2),c(1,2)).
    :- prec(c(1,2),a(1,1)), prec(a(1,1),a4(1,1)), prec(a4(1,1),c(1,2)).
    :- prec(c(1,2),a(1,1)), prec(a(1,1),a4(1,2)), prec(a4(1,2),c(1,2)).
    :- prec(c(1,2),a(1,1)), prec(a(1,1),a4(2,1)), prec(a4(2,1),c(1,2)).
    :- prec(c(1,2),a(1,1)), prec(a(1,1),a4(2,2)), prec(a4(2,2),c(1,2)).
    :- prec(c(1,2),a(1,2)), prec(a(1,2),a4(1,1)), prec(a4(1,1),c(1,2)).
    :- prec(c(1,2),a(1,2)), prec(a(1,2),a4(1,2)), prec(a4(1,2),c(1,2)).
    :- prec(c(1,2),a(1,2)), prec(a(1,2),a4(2,1)), prec(a4(2,1),c(1,2)).
    :- prec(c(1,2),a(1,2)), prec(a(1,2),a4(2,2)), prec(a4(2,2),c(1,2)).
    :- prec(c(1,1),a(2,1)), prec(a(2,1),a4(1,1)), prec(a4(1,1),c(1,1)).
    :- prec(c(1,1),a(2,1)), prec(a(2,1),a4(1,2)), prec(a4(1,2),c(1,1)).
    :- prec(c(1,1),a(2,1)), prec(a(2,1),a4(2,1)), prec(a4(2,1),c(1,1)).
    :- prec(c(1,1),a(2,1)), prec(a(2,1),a4(2,2)), prec(a4(2,2),c(1,1)).
    :- prec(c(1,1),a(2,2)), prec(a(2,2),a4(1,1)), prec(a4(1,1),c(1,1)).
    :- prec(c(1,1),a(2,2)), prec(a(2,2),a4(1,2)), prec(a4(1,2),c(1,1)).
    :- prec(c(1,1),a(2,2)), prec(a(2,2),a4(2,1)), prec(a4(2,1),c(1,1)).
    :- prec(c(1,1),a(2,2)), prec(a(2,2),a4(2,2)), prec(a4(2,2),c(1,1)).
    :- prec(c(1,1),a(1,1)), prec(a(1,1),a4(1,1)), prec(a4(1,1),c(1,1)).
    :- prec(c(1,1),a(1,1)), prec(a(1,1),a4(1,2)), prec(a4(1,2),c(1,1)).
    :- prec(c(1,1),a(1,1)), prec(a(1,1),a4(2,1)), prec(a4(2,1),c(1,1)).
    :- prec(c(1,1),a(1,1)), prec(a(1,1),a4(2,2)), prec(a4(2,2),c(1,1)).
    :- prec(c(1,1),a(1,2)), prec(a(1,2),a4(1,1)), prec(a4(1,1),c(1,1)).
    :- prec(c(1,1),a(1,2)), prec(a(1,2),a4(1,2)), prec(a4(1,2),c(1,1)).
    :- prec(c(1,1),a(1,2)), prec(a(1,2),a4(2,1)), prec(a4(2,1),c(1,1)).
    :- prec(c(1,1),a(1,2)), prec(a(1,2),a4(2,2)), prec(a4(2,2),c(1,1)).
    :- prec(c(2,2),a(2,1)), prec(a(2,1),a4(1,1)), prec(a4(1,1),c(2,2)).
    :- prec(c(2,2),a(2,1)), prec(a(2,1),a4(1,2)), prec(a4(1,2),c(2,2)).
    :- prec(c(2,2),a(2,1)), prec(a(2,1),a4(2,1)), prec(a4(2,1),c(2,2)).
    :- prec(c(2,2),a(2,1)), prec(a(2,1),a4(2,2)), prec(a4(2,2),c(2,2)).
    :- prec(c(2,2),a(2,2)), prec(a(2,2),a4(1,1)), prec(a4(1,1),c(2,2)).
    :- prec(c(2,2),a(2,2)), prec(a(2,2),a4(1,2)), prec(a4(1,2),c(2,2)).
    :- prec(c(2,2),a(2,2)), prec(a(2,2),a4(2,1)), prec(a4(2,1),c(2,2)).
    :- prec(c(2,2),a(2,2)), prec(a(2,2),a4(2,2)), prec(a4(2,2),c(2,2)).
    :- prec(c(2,2),a(1,1)), prec(a(1,1),a4(1,1)), prec(a4(1,1),c(2,2)).
    :- prec(c(2,2),a(1,1)), prec(a(1,1),a4(1,2)), prec(a4(1,2),c(2,2)).
    :- prec(c(2,2),a(1,1)), prec(a(1,1),a4(2,1)), prec(a4(2,1),c(2,2)).
    :- prec(c(2,2),a(1,1)), prec(a(1,1),a4(2,2)), prec(a4(2,2),c(2,2)).
    :- prec(c(2,2),a(1,2)), prec(a(1,2),a4(1,1)), prec(a4(1,1),c(2,2)).
    :- prec(c(2,2),a(1,2)), prec(a(1,2),a4(1,2)), prec(a4(1,2),c(2,2)).
    :- prec(c(2,2),a(1,2)), prec(a(1,2),a4(2,1)), prec(a4(2,1),c(2,2)).
    :- prec(c(2,2),a(1,2)), prec(a(1,2),a4(2,2)), prec(a4(2,2),c(2,2)).
    :- prec(c(2,1),a(2,1)), prec(a(2,1),a4(1,1)), prec(a4(1,1),c(2,1)).
    :- prec(c(2,1),a(2,1)), prec(a(2,1),a4(1,2)), prec(a4(1,2),c(2,1)).
    :- prec(c(2,1),a(2,1)), prec(a(2,1),a4(2,1)), prec(a4(2,1),c(2,1)).
    :- prec(c(2,1),a(2,1)), prec(a(2,1),a4(2,2)), prec(a4(2,2),c(2,1)).
    :- prec(c(2,1),a(2,2)), prec(a(2,2),a4(1,1)), prec(a4(1,1),c(2,1)).
    :- prec(c(2,1),a(2,2)), prec(a(2,2),a4(1,2)), prec(a4(1,2),c(2,1)).
    :- prec(c(2,1),a(2,2)), prec(a(2,2),a4(2,1)), prec(a4(2,1),c(2,1)).
    :- prec(c(2,1),a(2,2)), prec(a(2,2),a4(2,2)), prec(a4(2,2),c(2,1)).
    :- prec(c(2,1),a(1,1)), prec(a(1,1),a4(1,1)), prec(a4(1,1),c(2,1)).
    :- prec(c(2,1),a(1,1)), prec(a(1,1),a4(1,2)), prec(a4(1,2),c(2,1)).
    :- prec(c(2,1),a(1,1)), prec(a(1,1),a4(2,1)), prec(a4(2,1),c(2,1)).
    :- prec(c(2,1),a(1,1)), prec(a(1,1),a4(2,2)), prec(a4(2,2),c(2,1)).
    :- prec(c(2,1),a(1,2)), prec(a(1,2),a4(1,1)), prec(a4(1,1),c(2,1)).
    :- prec(c(2,1),a(1,2)), prec(a(1,2),a4(1,2)), prec(a4(1,2),c(2,1)).
    :- prec(c(2,1),a(1,2)), prec(a(1,2),a4(2,1)), prec(a4(2,1),c(2,1)).
    :- prec(c(2,1),a(1,2)), prec(a(1,2),a4(2,2)), prec(a4(2,2),c(2,1)).
    :- prec(c(1,2),a4(1,1)), prec(a4(1,1),a(2,1)), prec(a(2,1),c(1,2)).
    :- prec(c(1,2),a4(1,1)), prec(a4(1,1),a(2,2)), prec(a(2,2),c(1,2)).
    :- prec(c(1,2),a4(1,1)), prec(a4(1,1),a(1,1)), prec(a(1,1),c(1,2)).
    :- prec(c(1,2),a4(1,1)), prec(a4(1,1),a(1,2)), prec(a(1,2),c(1,2)).
    :- prec(c(1,2),a4(1,2)), prec(a4(1,2),a(2,1)), prec(a(2,1),c(1,2)).
    :- prec(c(1,2),a4(1,2)), prec(a4(1,2),a(2,2)), prec(a(2,2),c(1,2)).
    :- prec(c(1,2),a4(1,2)), prec(a4(1,2),a(1,1)), prec(a(1,1),c(1,2)).
    :- prec(c(1,2),a4(1,2)), prec(a4(1,2),a(1,2)), prec(a(1,2),c(1,2)).
    :- prec(c(1,2),a4(2,1)), prec(a4(2,1),a(2,1)), prec(a(2,1),c(1,2)).
    :- prec(c(1,2),a4(2,1)), prec(a4(2,1),a(2,2)), prec(a(2,2),c(1,2)).
    :- prec(c(1,2),a4(2,1)), prec(a4(2,1),a(1,1)), prec(a(1,1),c(1,2)).
    :- prec(c(1,2),a4(2,1)), prec(a4(2,1),a(1,2)), prec(a(1,2),c(1,2)).
    :- prec(c(1,2),a4(2,2)), prec(a4(2,2),a(2,1)), prec(a(2,1),c(1,2)).
    :- prec(c(1,2),a4(2,2)), prec(a4(2,2),a(2,2)), prec(a(2,2),c(1,2)).
    :- prec(c(1,2),a4(2,2)), prec(a4(2,2),a(1,1)), prec(a(1,1),c(1,2)).
    :- prec(c(1,2),a4(2,2)), prec(a4(2,2),a(1,2)), prec(a(1,2),c(1,2)).
    :- prec(c(1,1),a4(1,1)), prec(a4(1,1),a(2,1)), prec(a(2,1),c(1,1)).
    :- prec(c(1,1),a4(1,1)), prec(a4(1,1),a(2,2)), prec(a(2,2),c(1,1)).
    :- prec(c(1,1),a4(1,1)), prec(a4(1,1),a(1,1)), prec(a(1,1),c(1,1)).
    :- prec(c(1,1),a4(1,1)), prec(a4(1,1),a(1,2)), prec(a(1,2),c(1,1)).
    :- prec(c(1,1),a4(1,2)), prec(a4(1,2),a(2,1)), prec(a(2,1),c(1,1)).
    :- prec(c(1,1),a4(1,2)), prec(a4(1,2),a(2,2)), prec(a(2,2),c(1,1)).
    :- prec(c(1,1),a4(1,2)), prec(a4(1,2),a(1,1)), prec(a(1,1),c(1,1)).
    :- prec(c(1,1),a4(1,2)), prec(a4(1,2),a(1,2)), prec(a(1,2),c(1,1)).
    :- prec(c(1,1),a4(2,1)), prec(a4(2,1),a(2,1)), prec(a(2,1),c(1,1)).
    :- prec(c(1,1),a4(2,1)), prec(a4(2,1),a(2,2)), prec(a(2,2),c(1,1)).
    :- prec(c(1,1),a4(2,1)), prec(a4(2,1),a(1,1)), prec(a(1,1),c(1,1)).
    :- prec(c(1,1),a4(2,1)), prec(a4(2,1),a(1,2)), prec(a(1,2),c(1,1)).
    :- prec(c(1,1),a4(2,2)), prec(a4(2,2),a(2,1)), prec(a(2,1),c(1,1)).
    :- prec(c(1,1),a4(2,2)), prec(a4(2,2),a(2,2)), prec(a(2,2),c(1,1)).
    :- prec(c(1,1),a4(2,2)), prec(a4(2,2),a(1,1)), prec(a(1,1),c(1,1)).
    :- prec(c(1,1),a4(2,2)), prec(a4(2,2),a(1,2)), prec(a(1,2),c(1,1)).
    :- prec(c(2,2),a4(1,1)), prec(a4(1,1),a(2,1)), prec(a(2,1),c(2,2)).
    :- prec(c(2,2),a4(1,1)), prec(a4(1,1),a(2,2)), prec(a(2,2),c(2,2)).
    :- prec(c(2,2),a4(1,1)), prec(a4(1,1),a(1,1)), prec(a(1,1),c(2,2)).
    :- prec(c(2,2),a4(1,1)), prec(a4(1,1),a(1,2)), prec(a(1,2),c(2,2)).
    :- prec(c(2,2),a4(1,2)), prec(a4(1,2),a(2,1)), prec(a(2,1),c(2,2)).
    :- prec(c(2,2),a4(1,2)), prec(a4(1,2),a(2,2)), prec(a(2,2),c(2,2)).
    :- prec(c(2,2),a4(1,2)), prec(a4(1,2),a(1,1)), prec(a(1,1),c(2,2)).
    :- prec(c(2,2),a4(1,2)), prec(a4(1,2),a(1,2)), prec(a(1,2),c(2,2)).
    :- prec(c(2,2),a4(2,1)), prec(a4(2,1),a(2,1)), prec(a(2,1),c(2,2)).
    :- prec(c(2,2),a4(2,1)), prec(a4(2,1),a(2,2)), prec(a(2,2),c(2,2)).
    :- prec(c(2,2),a4(2,1)), prec(a4(2,1),a(1,1)), prec(a(1,1),c(2,2)).
    :- prec(c(2,2),a4(2,1)), prec(a4(2,1),a(1,2)), prec(a(1,2),c(2,2)).
    :- prec(c(2,2),a4(2,2)), prec(a4(2,2),a(2,1)), prec(a(2,1),c(2,2)).
    :- prec(c(2,2),a4(2,2)), prec(a4(2,2),a(2,2)), prec(a(2,2),c(2,2)).
    :- prec(c(2,2),a4(2,2)), prec(a4(2,2),a(1,1)), prec(a(1,1),c(2,2)).
    :- prec(c(2,2),a4(2,2)), prec(a4(2,2),a(1,2)), prec(a(1,2),c(2,2)).
    :- prec(c(2,1),a4(1,1)), prec(a4(1,1),a(2,1)), prec(a(2,1),c(2,1)).
    :- prec(c(2,1),a4(1,1)), prec(a4(1,1),a(2,2)), prec(a(2,2),c(2,1)).
    :- prec(c(2,1),a4(1,1)), prec(a4(1,1),a(1,1)), prec(a(1,1),c(2,1)).
    :- prec(c(2,1),a4(1,1)), prec(a4(1,1),a(1,2)), prec(a(1,2),c(2,1)).
    :- prec(c(2,1),a4(1,2)), prec(a4(1,2),a(2,1)), prec(a(2,1),c(2,1)).
    :- prec(c(2,1),a4(1,2)), prec(a4(1,2),a(2,2)), prec(a(2,2),c(2,1)).
    :- prec(c(2,1),a4(1,2)), prec(a4(1,2),a(1,1)), prec(a(1,1),c(2,1)).
    :- prec(c(2,1),a4(1,2)), prec(a4(1,2),a(1,2)), prec(a(1,2),c(2,1)).
    :- prec(c(2,1),a4(2,1)), prec(a4(2,1),a(2,1)), prec(a(2,1),c(2,1)).
    :- prec(c(2,1),a4(2,1)), prec(a4(2,1),a(2,2)), prec(a(2,2),c(2,1)).
    :- prec(c(2,1),a4(2,1)), prec(a4(2,1),a(1,1)), prec(a(1,1),c(2,1)).
    :- prec(c(2,1),a4(2,1)), prec(a4(2,1),a(1,2)), prec(a(1,2),c(2,1)).
    :- prec(c(2,1),a4(2,2)), prec(a4(2,2),a(2,1)), prec(a(2,1),c(2,1)).
    :- prec(c(2,1),a4(2,2)), prec(a4(2,2),a(2,2)), prec(a(2,2),c(2,1)).
    :- prec(c(2,1),a4(2,2)), prec(a4(2,2),a(1,1)), prec(a(1,1),c(2,1)).
    :- prec(c(2,1),a4(2,2)), prec(a4(2,2),a(1,2)), prec(a(1,2),c(2,1)).

    %[COMMENT]: Global SAT and (un)found rules.
    :- not sat.
    sat :- sat_r4.
    :- r4_4_unfound(1,2), a4(2,1).
    :- r4_4_unfound(2,1), a4(1,2).
    :- r4_4_unfound(1,1), a4(1,1).
    :- r4_4_unfound(2,2), a4(2,2).
    :- a4(2,1), #sum{1,0 : r4_unfound(2,1)} >=1 .
    :- a4(1,1), #sum{1,0 : r4_unfound(1,1)} >=1 .
    :- a4(2,2), #sum{1,0 : r4_unfound(2,2)} >=1 .
    :- a4(1,2), #sum{1,0 : r4_unfound(1,2)} >=1 .

    %[COMMENT]: Final show statements.
    #show d/1.
    #show c/2.
    #show a/2.

Although the above program is significantly larger, for certain scenarios it actually outperforms the *shared-cycle-body-predicates*,
especially for *dense* bodies, where *dense* means a body with many variables, which would have to be grounded by a complete enumeration,
and the maximum arity of the literals is low.
Note that the output is still correct:

.. code-block:: console

    $ clingo --project --model 0 output.lp 
    clingo version 5.6.2
    Reading from output.lp
    Solving...
    Answer: 1
    d(1) c(1,2) c(1,1) a(2,1) a(1,1) a(1,2) c(2,1)
    SATISFIABLE

    Models       : 1
    Calls        : 1
    Time         : 0.020s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
    CPU Time     : 0.013s




           