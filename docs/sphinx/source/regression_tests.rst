Regression Tests
================

**TODO**

A script is provided to execute regression tests (`start_regression_tests.py`), which checks if the output of given programs is the same for hybrid_grounding and for Clingo. To be more specific, it checks if every answer set that occurs in the output of hybrid_grounding also occurs in the Answer set of Clingo, and vice versa.

The regression tests can be found in the folder `regression_tests`, where the `regression_tests/test_instances` features all currently implemented regression tests. The executed tests consist of a variety of tests, both with and without Aggregates.

It can be executed with:

```
$ python3 start_regression_tests.py <TEST-FOLDER>
```

So e.g.:

```
$ python3 start_regression_tests.py regression_tests/test_instances
```


### Some Assumptions

- For all RS-Rewriting strategies for an aggregate ''#agg{E} = Z'', we expect ''Z'' to either be an integer constant or a BOUND variable. 
- For the SUM RS-Rewriting strategies we assume (>=0) values at each first term-element-head position (so for #sum{X,Y : a(X,Y),...;....} >= 5. all X-values are required to be >=0).


## Usage (with installation)

```
$ hybrid_grounding -h
usage: hybrid_grounding [files]

positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  --no-show             Do not print #show-statements to avoid compatibility issues.
  --ground-guess        Additionally ground guesses which results in (fully) grounded output.
  --ground              Output program fully grounded.
  --aggregate-strategy {replace,rewrite,rewrite-no-body}
```

