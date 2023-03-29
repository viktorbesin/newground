vertex(1).
vertex(2).
vertex(3).
vertex(4).
vertex(5).
vertex(6).
vertex(7).
vertex(8).
vertex(9).
edge(1,2).
edge(1,3).
edge(1,6).
edge(1,9).
edge(2,5).
edge(2,7).
edge(3,1).
edge(3,3).
edge(3,4).
edge(4,1).
edge(4,4).
edge(4,5).
edge(4,7).
edge(4,8).
edge(4,9).
edge(5,2).
edge(5,3).
edge(5,5).
edge(5,6).
edge(5,7).
edge(5,8).
edge(5,9).
edge(6,1).
edge(6,3).
edge(6,6).
edge(6,7).
edge(7,1).
edge(7,2).
edge(7,3).
edge(7,4).
edge(7,7).
edge(7,8).
edge(8,1).
edge(8,3).
edge(8,4).
edge(8,5).
edge(9,1).
edge(9,4).
edge(9,5).
edge(9,6).
edge(9,7).
edge(9,9).


violation(X,Y) :- edge(X,Y), g(X), g(Y).
violation(X,Y) :- edge(X,Y), b(X), b(Y).
violation(X,Y) :- edge(X,Y), r(X), r(Y).

violation_2(Y2,X2) :- violation(X,Y), X2 = 2 * X, Y2 = 2 * Y.
violation_3(X3,Y3) :- violation(X,Y), X3 = 4 * X, Y3 = 4 * Y.

x(X) :- vertex(X).
g(X) :- x(X), not g_1(X).
g_1(X) :- vertex(X), not g(X).

r(X) :- x(X), not r_1(X).
r_1(X) :- vertex(X), not r(X).

b(X) :- x(X), not b_1(X).
b_1(X) :- vertex(X), not b(X).

:- g(X), r(X).
:- g(X), b(X).
:- r(X), b(X).
:- vertex(X), not g(X), not r(X), not b(X).

