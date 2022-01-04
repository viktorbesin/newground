# newground
Reduction of **non-ground** logic programs to **disjunctive** logic programs using body-decoupled grounding.

## Requirements
* clingo 
* clingo's Python module > *v5.5*
* clingox
* future-fstrings (for compatibility with older versions)
```
pip install -r requirements.txt
```

## Input Format
The input format is equivalent to clingos input format. Currently the reduction of normal logic programs (including comparison operators) is implemented. 

Based on the principle of partial reducability, inputs can be divided into parts that shall be part of the reduction. For this reason please use `#program rules.` for (non-ground) program parts that shall be reduced by **newground**. The sub-program `#program insts.` on the other hand can be used for instantiating the program.

Without explicit domains given the reduction uses the complete set of terms to fill the variables in the grounding process. This process can be reduced by giving a domain for each variable, e.g. `_dom_X(1..5).`, or by `_dom_X(X) :- a(X,_).` in the instatiating-part of the program. This information is then processed automatically and considered in the reduction.

## Usage
```
$ python3 main.py -h
usage: newground [files]

positional arguments:
  file

optional arguments:
  -h, --help      show this help message and exit
  --no-show       Do not print #show-statements to avoid compatibility issues.
  --ground-guess  Additionally ground guesses which results in (fully) grounded output.
  --ground        Output program fully grounded.
```