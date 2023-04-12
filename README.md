# newground

Reduction of **non-ground** logic programs to **disjunctive** logic programs using body-decoupled grounding, extended by Aggregates. This is the prototype, which is mentioned in the paper: Viktor Besin, Markus Hecher, and Stefan Woltran. Body-decoupled grounding via solving: A novel approach on the asp bottleneck. In Lud De Raedt, editor, Proceedings of the Thirty-First International Joint Conference on Artificial Intelligence, IJCAI-22, pages 2546–2552. International Joint Conferences on Artificial Intelligence Organization, 7 2022. Main Track. [LINK](https://www.ijcai.org/proceedings/2022/353).

Note that the prototype mentioned in the paper does not include Aggregates. The extension of Newground by Aggregates is part of a Bachelor's Thesis.

## Requirements
* clingo 
* clingo's Python module > *v5.6*
* clingox
* networkx
* future-fstrings (for compatibility with older versions)

## Input Format
The input format is a subset to clingos input format. The subset that works consists of:
- Rules with predicates (and no other special language constructs), where the terms in the predicates only consist of variables or integer constants.
- Comparisons instead of predicates in the body
- Aggregates, where the lower/upper bounds are integer constants

Based on the principle of partial reducability, inputs can be divided into parts that shall be part of the reduction. For this reason please use `#program rules.` for (non-ground) program parts that shall be reduced by **newground**. The sub-program `#program insts.` on the other hand can be used for instantiating the program.

Without explicit domains given the reduction uses the complete set of terms to fill the variables in the grounding process. This process can be reduced by giving a domain for each variable, e.g. `_dom_X(1..5).`, or by `_dom_X(X) :- a(X,_).` in the instatiating-part of the program. This information is then processed automatically and considered in the reduction.

## Usage (no installation)
```
$ python start_newground.py -h
usage: newground [files]

positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  --no-show             Do not print #show-statements to avoid compatibility issues.
  --ground-guess        Additionally ground guesses which results in (fully) grounded output.
  --ground              Output program fully grounded.
  --aggregate-strategy {replace,rewrite,rewrite-no-body}
```
e.g. clingo can then be used to compute the answer-sets
```
$ python start_newground.py [instance] | clingo -n 0 --project
```

## Installation
OPTIONAL: Note, that you do not need to install the package in order to use it! Installation is currently just possible in linux (and possibly MacOS) and just has the benefit to use it in the Linux command line from every location.

One can install newground in Linux in the environment, such that one can execute it through the command line

```
$ python setup.py install
```

If you have the `make` environment installed, you can use 

```
$ make
```

to install newground and 

```
$ make clean
```

to uninstall newground. 


## Usage (with installation)

```
$ newground -h
usage: newground [files]

positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  --no-show             Do not print #show-statements to avoid compatibility issues.
  --ground-guess        Additionally ground guesses which results in (fully) grounded output.
  --ground              Output program fully grounded.
  --aggregate-strategy {replace,rewrite,rewrite-no-body}
```

## Uninstall

```
$ pip uninstall newground
```

# Experiments

## Preliminary Setup (UNIX)

Prelminary setup (only applies for Unix-style systems, other systems not described here):
- (If not already done) Install clingo, python3 and idlv
- Find out the location of the respective binary files
- Create symbolic links to the respective binary files, and move the symbolic links to this repository (top-level, next to the `start_benchmark_tests.py`/`start_bounds_benchmark_tests.py` files)
- Name the symbolic links in the following way:
    - `clingo` for Clingo
    - `gringo` for gringo the grounder (is typically installed in conjunction with Clingo=
    - `idlv` for `IDLV`
    - `python3` for Python3

For the experiments two experiment scripts are provided, namely `start_benchmark_tests.py` and `start_bounds_benchmark_tests.py`. The former one is the ''standard'', experiment script, which has the following SYNAPSIS

## Standard Experiments

```
$ python3 start_benchmark_tests.py <BENCHMARK_DIRECTORY> <OUTPUT_FILES_PREFIX>
```

The benchmark directory (`<BENCHMARK_DIRECTORY>`) must be a directory, where at least the following files are present:

- `encoding.lp` -> Which encodes the problem. For the Newground grounder it holds, that the whole encoding file is prefixed with a `#program rules.`.
- `instance_X.lp` -> Which denotes one instance. Note that all files that match the regex `^instance_[0-9]{1,4}\.lp$` are considered to be a valid instance.
- `additional_instance.lp` -> Additional parts of the instance, that shall be used for every instance.


The `<OUTPUT_FILES_PREFIX>` then specifies how the output-files should be prefixed. Note that three files are generated (`<OUTPUT_FILE_PREFIX>_total_time.csv`,`<OUTPUT_FILE_PREFIX>_grounding_time.csv` and `<OUTPUT_FILE_PREFIX>_grounding_size.csv`).

Important note: The rewriting strategy can at the time of writing, only be changed in the python file directly (`self.rewriting_strategy`), defined in the `__init__` method of the `Benchmark` class.

### Benchmark Files

Example benchmark files can be found in `instances/benchmark/`. These files also constitute the experiments that were performed in the thesis, but note that the following change in notation applies:

- `clique_3_light_head` -> `ALPC3`
- `clique_3_heavy_head` -> `AHPC3`
- `clique_9_light_head` -> `ALL9`
- `clique_9_heavy_head` -> `AHL9`

Note that the instance files (the `instance_X.lp` files) have been deleted from the benchmarks and can be found in the `generators` folder (`generators/graphs` for the graph instances and `generators/marriages` for the Stable Marriage problem).

### Example

```
$ python3 start_bounds_benchmark_tests.py test-output instances/benchmark/count_clique_3_light_head/additional_instance.lp generators/graphs/instance_0004.lp 
```

## Bounds Script

The bounds script, i.e. the `start_bounds_benchmark_tests.py` script, executes the experiments, where one fixes an instance and an additional instance, and then executes the `ALL9` problem by continously increasing the lower bound of the aggregate. It can be executd with:

```
$ python3 start_bounds_benchmark_tests.py <OUTPUT_FILES_PREFIX> [<INSTANCE_FILES>]
```

### Example

```
$ python3 start_bounds_benchmark_tests.py test-output instances/benchmark/count_clique_3_light_head/additional_instance.lp generators/graphs/instance_0004.lp 
```


# Regression Tests

A script is provided to execute regression tests (`start_regression_tests.py`), which checks if the output of given programs is the same for Newground and for Clingo. To be more specific, it checks if every answer set that occurs in the output of Newground also occurs in the Answer set of Clingo, and vice versa.

The regression tests can be found in the folder `regression_tests`, where the `regression_tests/test_instances` features all currently implemented regression tests. The executed tests consist of a variety of tests, both with and without Aggregates.

It can be executed with:

```
$ python3 start_regression_tests.py <TEST-FOLDER>
```

So e.g.:

```
$ python3 start_regression_tests.py regression_tests/test_instances
```





