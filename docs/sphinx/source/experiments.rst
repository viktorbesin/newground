Experiments
============

**TODO**

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

- `encoding.lp` -> Which encodes the problem. For the hybrid_grounding grounder it holds, that the whole encoding file is prefixed with a `#program rules.`.
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

