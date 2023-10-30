Going into more Depth
======================

Input Format
------------

The input format is a subset to clingos input format. The subset that works consists of:

- Rules with predicates (and no other special language constructs), where the terms in the predicates only consist of variables or integer constants.
- Comparisons instead of predicates in the body
- Aggregates, where the lower/upper bounds are integer constants

Based on the principle of partial reducability, inputs can be divided into parts that shall be part of the reduction. For this reason please use `#program rules.` for (non-ground) program parts that shall be reduced by **hybrid_grounding**. The sub-program `#program insts.` on the other hand can be used for instantiating the program.

Without explicit domains given the reduction uses the complete set of terms to fill the variables in the grounding process. This process can be reduced by giving a domain for each variable, e.g. `_dom_X(1..5).`, or by `_dom_X(X) :- a(X,_).` in the instatiating-part of the program. This information is then processed automatically and considered in the reduction.

Synapsis
-----------

By entering enter, you are able to 

.. code-block:: console

    $ hybrid_grounding --help    
    usage: hybrid_grounding [files]

    positional arguments:
      files

    options:
      -h, --help            show this help message and exit
      --no-show             Do not print #show-statements to avoid compatibility issues.
      --mode {rewrite-aggregates-ground-partly,rewrite-aggregates-no-ground,rewrite-aggregates-ground-fully}
      --aggregate-strategy {RA,RS,RS-PLUS,RS-STAR,RECURSIVE}
      --cyclic-strategy {assume-tight,level-mappings,shared-cycle-body-predicates,level-mappings-AAAI}

