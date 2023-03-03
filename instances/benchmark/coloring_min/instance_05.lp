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

1 <= {g(X); b(X); r(X)} <= 1 :- vertex(X).

violation(X,Y) :- edge(X,Y), g(X), g(Y).
violation(X,Y) :- edge(X,Y), b(X), b(Y).
violation(X,Y) :- edge(X,Y), r(X), r(Y).

violation_2(Y2,X2) :- violation(X,Y), X2 = 2 * X, Y2 = 2 * Y.
violation_3(X3,Y3) :- violation(X,Y), X3 = 4 * X, Y3 = 4 * Y.


