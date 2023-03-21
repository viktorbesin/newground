# newground
Reduction of **non-ground** logic programs to **disjunctive** logic programs using body-decoupled grounding.

## Requirements
* clingo 
* clingo's Python module > *v5.5*
* clingox
* networkx
* future-fstrings (for compatibility with older versions)
```
pip install -r requirements.txt
```

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

