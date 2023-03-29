vertex(1).
vertex(2).
vertex(3).
vertex(4).
edge(1,1).
edge(1,3).
edge(2,1).
edge(2,2).
edge(3,2).
edge(3,3).
edge(4,2).
edge(4,3).


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

