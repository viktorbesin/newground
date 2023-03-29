vertex(1).
vertex(2).
vertex(3).
vertex(4).
edge(1,3).
edge(2,3).
edge(2,4).
edge(3,1).
edge(3,2).
edge(3,3).
edge(3,4).
edge(4,4).

set_count(1).
set_count(2).
set_count(3).
set_count(4).
set_count(5).

x(X) :- vertex(X). % Not really needed

set(X,S) :- set_count(S), x(X), not set_not(X,S).
set_not(X,S) :- set_count(S), x(X), not set(X,S).

:- set(X1,S1), set(X2,S2), X1 = X2, S1 != S2.  

