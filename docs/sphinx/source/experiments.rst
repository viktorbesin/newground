Experiments
============

For the source code of the experiments, the experimental instances, etc., take a look at the experiments repository experiments-page_
For other additional information, not found here, take a look at the relevant publications.

.. _experiments-page: https://github.com/alexl4123/newground-experiments

Methodology:
---------------

We mainly measure grounding sizes (times) and combined times
(grounding and solving). Grounding size thereby refers to the output size, which is ei-
ther in smodels or aspif format for idlv and gringo, respectively. In our benchmarks,
we limit available main memory (RAM) to 32GB (for each grounding or solving), and
the overall runtime for both grounding and solving to 1800s. The plots used in this pa-
per only show grounding sizes up to 32GB. We used a cluster, where each node has an
AMD Opteron 6272 with 225GB RAM on Debian10 with kernel 4.19.0-16-amd64.


Benchmark instances
----------------------

- S1 **Polygamy Stable Matching:** We adapt the *stable marriage* problem, where we allow polygamy for some individual. 
- S2 **Relaxed NPRC:** We relax non-partition-removal colorings (1_), where we allow some deleted node causing a disconnected graph.
- S3 **Traffic Connector Nodes:** Decide whether there are connected subgraphs reaching the majority of the nodes, such that we use at most one central node of degree *>= k*. We let *k* range from 4 (*S3-T4*), 6 (S3-T6), to 8 (*S3-T8*). 
- S4 **Count Traffic Connectors:** Similar to *S3*, but we count (minimize) the number of traffic connectors. As above, *k* ranges from 4 (*S4-T4*), 6 (*S4-T6*) to 8 (*S4-T8*).
 
The version of S1 and S2 without aggregates are known ASP scenarios. S3 and S4 are real-world inspired examples. 
For S1 - S3 and S4, we use *RS* and *RA*, respectively. 

.. _1: https://arxiv.org/abs/2008.03526

Further every benchmark instance is divided into three files:

1. Encoding file *encoding.lp*: Is the encoding, that is grounded via newground/BDG.
2. Instance file *instance.lp* (name may diverge from problem to problem): Is a file of facts, which determines the current problem instance.
3. Encoding file *additional_instance.lp*: Is the encoding/additional-instance file, which is grounded via traditional-means.

In the following the *encoding.lp* and *additional_instance.lp* file-contents are given, and additionally a toy instance is provided.

S1 **Polygamy Stable Matching**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*encoding.lp*:

.. code-block::

    :- 2 <= #count{W : match(M1,W), match(M2,W), match(M3,W), M1 != M2, M1 != M3, M2 != M3}.
    :- 2 <= #count{M : match(M,W1), match(M,W2), match(M,W3), W1 != W2, W1 != W3, W2 != W3}.

*additional-instance.lp*:

.. code-block::

    % guess matching
    match(M,W) :- manAssignsScore(M,_,_), womanAssignsScore(W,_,_), not nonMatch(M,W).
    nonMatch(M,W) :- manAssignsScore(M,_,_), womanAssignsScore(W,_,_), not match(M,W).
    % no singles
    jailed(M) :- match(M,_).
    :- manAssignsScore(M,_,_), not jailed(M).
    % strong stability condition
    :- match(M,W1), manAssignsScore(M,W,Smw), W1 != W, manAssignsScore(M,W1,Smw1), Smw > Smw1, match(M1,W), womanAssignsScore(W,M,Swm), womanAssignsScore(W,M1,Swm1), Swm >= Swm1.

*toy-instance.lp*:

.. code-block::

    manAssignsScore(1,1,1).
    womanAssignsScore(1,1,1).

S2 **Relaxed NPRC** 
^^^^^^^^^^^^^^^^^^^^^^^^

*encoding.lp*:

.. code-block::

    :- 2 <= #count{D : delete(D), edge(V1,D), edge(D, V2), not reachable(V1, V2)}.

*additional-instance.lp*:

.. code-block::

    keep(X) :- vertex(X), not delete(X).
    delete(X) :- vertex(X), not keep(X).
    :- delete(X), vertex(Y), not keep(Y), X != Y.

    kept_edge(V1, V2) :- keep(V1), keep(V2), edge(V1, V2).
    reachable(X, Y) :- kept_edge(X, Y).

    blue(N) :- keep(N), not red(N), not green(N).
    red(N) :- keep(N), not blue(N), not green(N).
    green(N) :- keep(N), not red(N), not blue(N).

    :- kept_edge(N1,N2), blue(N1), blue(N2).
    :- kept_edge(N1,N2), red(N1), red(N2).
    :- kept_edge(N1,N2), green(N1), green(N2).

    reachable(X, Z) :- delete(D), edge(X, D), reachable(X, Y), reachable(Y, Z).

*toy-instance.lp*:

.. code-block::

    vertex(1).
    vertex(2).
    vertex(3).
    vertex(4).

    edge(1,2).
    edge(2,3).
    edge(3,4).
    edge(4,1).

S3 **Traffic Connector Nodes:**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*encoding.lp* (S3-T4):

.. code-block::

    :- 2 <= #count{A : f(A,B), f(A,C), f(A,D), f(A,E), A != B, A != C, A != D, A != E, B != C, B != D, B != E, C != D, C != E, D != E}.

*additional-instance.lp*:

.. code-block::

    {f(X,Y)} :- edge(X,Y).

    rch(X) :- X = #min{A: f(A,_); B: f(_,B)}.
    rch(Y) :- rch(X), f(X,Y).
    rch(X) :- rch(Y), f(X,Y).

    :- #count{X: rch(X)} < M, min_reached_vertices(M).

    % Graph must be connected
    :- f(X,Y), not rch(X).

*toy-instance*:

.. code-block::

    edge(1,2).
    edge(2,3).
    edge(3,4).
    edge(4,1).
    min_reached_vertices(4).
       

S4 **Count Traffic Connectors:** 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For *S4* we just display the *encoding.lp*, as the *additional_instance.lp* and *toy-instance.lp* are the same.

*encoding.lp* (S4-T4):

.. code-block::
    
    d(X) :- X = #count{A : f(A,B), f(A,C), f(A,D), f(A,E), A != B, A != C, A != D, A != E, B != C, B != D, B != E, C != D, C != E, D != E}.


A note on the benchmark scripts:
-----------------------------------

*start_benchmark_tests.py*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The main benchmark script is the *start_benchmark_tests.py* script.
It assumes *gringo*, *clingo*, *idlv.bin* and *python3* as binaries on the same level as the script.
Further, it assumes newground (*start_newground.py*) to be on the same level as the script.
This can in general be changed at the bottom of the file (look for the *config* dict).
You can also change the aggregate **rewriting_strategy** there (and add possible other config-infos, but where maybe additional coding is necessary).

On a very high level the script calls multiple other scripts, as subprocesses.
These subprocess-scripts then call the relevant-grounders and solvers.

The **synapsis** of the benchmark script are two positional arguments:

1. **input_folder**: Here reside the *encoding.lp*, the *additional_instance.lp* file and the (multiple) *instace* files (note that the *encoding.lp* and *additional_instance.lp* files have to be exactly named like that, but the *instance* files might have other names).
2. **output_file**: Which stores the output results. Note to only give a file-stem (e.g. instead of *output.csv* only *output*), as different measures are tracked in multiple files.

The script then calls each instance-file in order.
For each such file it first performs a *GRINGO*, a *IDLV*, a *newground-IDLV*, and a *newground-GRINGO* run (**not necessarily in this order!**).

*start_benchmark_.py* files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Are helper scripts of the main *start_benchmark_tests.py* file.
They include utils files (like base64 encodings for passing arguments), and files for specific grounder-strategies.

*start_script_*.sh* files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Are most of the time actually used to start the *start_benchmark_tests.py* file, as they are able to start multiple runs in parallel, e.g., for computing density measures (grounding-profile).


