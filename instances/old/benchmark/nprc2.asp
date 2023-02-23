vertex(X) :- edge(X,_).
vertex(Y) :- edge(_,Y).
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

#program rules.
:- delete(D), edge(V1, D), edge(D, V2), not reachable(V1, V2).
