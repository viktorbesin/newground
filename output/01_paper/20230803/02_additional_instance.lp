{f(X,Y)} :- edge(X,Y).

rch(X) :- X = #min{A: f(A,_); B: f(_,B)}.
rch(Y) :- rch(X), f(X,Y).
rch(X) :- rch(Y), f(X,Y).

:- #count{X: rch(X)} < M, min_reached_vertices(M).

% Graph must be connected
:- f(X,Y), not rch(X).



