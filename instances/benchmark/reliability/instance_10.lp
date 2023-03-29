vertex(1).
vertex(2).
vertex(3).
vertex(4).
vertex(5).
vertex(6).
vertex(7).
vertex(8).
vertex(9).
edge(1,1).
edge(1,3).
edge(1,7).
edge(2,5).
edge(2,6).
edge(2,7).
edge(2,8).
edge(2,9).
edge(3,3).
edge(3,6).
edge(3,7).
edge(3,9).
edge(4,4).
edge(4,6).
edge(4,9).
edge(5,1).
edge(5,4).
edge(5,7).
edge(5,9).
edge(6,1).
edge(6,2).
edge(6,8).
edge(6,9).
edge(7,2).
edge(7,4).
edge(7,5).
edge(7,6).
edge(7,7).
edge(7,8).
edge(8,6).
edge(8,8).
edge(9,1).
edge(9,3).
edge(9,5).
edge(9,8).
edge(9,9).

set_count(1).
set_count(2).
set_count(3).
set_count(4).
set_count(5).

x(X) :- vertex(X). % Not really needed

set(X,S) :- set_count(S), x(X), not set_not(X,S).
set_not(X,S) :- set_count(S), x(X), not set(X,S).

:- set(X1,S1), set(X2,S2), X1 = X2, S1 != S2.  

