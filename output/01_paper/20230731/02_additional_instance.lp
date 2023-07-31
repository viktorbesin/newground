{f(X,Y)} :- edge(X,Y).

rch(X) :- X = #min{A: f(A,_); B: f(_,B)}.
rch(Y) :- rch(X), f(X,Y).
rch(X) :- rch(Y), f(X,Y).

% Graph must be connected
:- f(X,Y), not rch(X).


