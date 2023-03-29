vertex(1).
vertex(2).
vertex(3).
vertex(4).
vertex(5).
vertex(6).
vertex(7).
vertex(8).
vertex(9).
vertex(10).
vertex(11).
vertex(12).
vertex(13).
vertex(14).
edge(1,1).
edge(1,4).
edge(1,5).
edge(1,6).
edge(1,7).
edge(1,8).
edge(1,9).
edge(1,10).
edge(1,12).
edge(1,14).
edge(2,1).
edge(2,3).
edge(2,7).
edge(2,8).
edge(2,9).
edge(3,1).
edge(3,2).
edge(3,4).
edge(3,5).
edge(3,8).
edge(3,11).
edge(4,1).
edge(4,4).
edge(4,9).
edge(4,10).
edge(4,11).
edge(4,13).
edge(4,14).
edge(5,5).
edge(5,6).
edge(5,12).
edge(5,13).
edge(6,1).
edge(6,2).
edge(6,3).
edge(6,6).
edge(6,9).
edge(6,10).
edge(6,13).
edge(6,14).
edge(7,2).
edge(7,3).
edge(7,6).
edge(7,9).
edge(7,11).
edge(7,12).
edge(7,13).
edge(8,1).
edge(8,3).
edge(8,5).
edge(8,7).
edge(8,8).
edge(8,10).
edge(8,12).
edge(8,13).
edge(9,5).
edge(9,7).
edge(9,10).
edge(9,11).
edge(9,13).
edge(10,2).
edge(10,3).
edge(10,4).
edge(10,6).
edge(10,8).
edge(10,11).
edge(10,14).
edge(11,1).
edge(11,2).
edge(11,3).
edge(11,4).
edge(11,9).
edge(11,12).
edge(12,3).
edge(12,4).
edge(12,5).
edge(12,12).
edge(13,1).
edge(13,2).
edge(13,4).
edge(13,5).
edge(13,6).
edge(13,7).
edge(13,8).
edge(14,3).
edge(14,5).
edge(14,6).
edge(14,9).
edge(14,11).
edge(14,12).
edge(14,14).

1 <= {g(X); b(X); r(X)} <= 1 :- vertex(X).

violation(X,Y) :- edge(X,Y), g(X), g(Y).
violation(X,Y) :- edge(X,Y), b(X), b(Y).
violation(X,Y) :- edge(X,Y), r(X), r(Y).

violation_2(Y2,X2) :- violation(X,Y), X2 = 2 * X, Y2 = 2 * Y.
violation_3(X3,Y3) :- violation(X,Y), X3 = 4 * X, Y3 = 4 * Y.


