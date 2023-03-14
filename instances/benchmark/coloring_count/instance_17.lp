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
vertex(15).
vertex(16).
edge(1,5).
edge(1,6).
edge(1,7).
edge(1,12).
edge(1,13).
edge(1,14).
edge(1,15).
edge(1,16).
edge(2,3).
edge(2,5).
edge(2,6).
edge(2,7).
edge(2,8).
edge(2,10).
edge(2,11).
edge(2,12).
edge(2,13).
edge(2,14).
edge(2,15).
edge(2,16).
edge(3,1).
edge(3,2).
edge(3,3).
edge(3,4).
edge(3,5).
edge(3,6).
edge(3,7).
edge(3,8).
edge(3,10).
edge(3,11).
edge(3,16).
edge(4,2).
edge(4,4).
edge(4,5).
edge(4,7).
edge(4,8).
edge(4,9).
edge(4,11).
edge(4,12).
edge(4,13).
edge(4,15).
edge(4,16).
edge(5,1).
edge(5,4).
edge(5,5).
edge(5,6).
edge(5,7).
edge(5,8).
edge(5,9).
edge(5,10).
edge(5,11).
edge(5,12).
edge(5,13).
edge(5,15).
edge(6,4).
edge(6,5).
edge(6,7).
edge(6,9).
edge(6,10).
edge(6,14).
edge(6,15).
edge(6,16).
edge(7,2).
edge(7,3).
edge(7,4).
edge(7,6).
edge(7,7).
edge(7,9).
edge(7,10).
edge(7,11).
edge(7,12).
edge(7,13).
edge(8,1).
edge(8,3).
edge(8,4).
edge(8,5).
edge(8,9).
edge(8,10).
edge(8,11).
edge(8,12).
edge(8,14).
edge(8,15).
edge(8,16).
edge(9,1).
edge(9,2).
edge(9,4).
edge(9,9).
edge(9,10).
edge(10,2).
edge(10,3).
edge(10,4).
edge(10,5).
edge(10,8).
edge(10,9).
edge(10,13).
edge(10,15).
edge(11,1).
edge(11,4).
edge(11,8).
edge(11,9).
edge(11,10).
edge(11,12).
edge(11,13).
edge(11,15).
edge(11,16).
edge(12,2).
edge(12,3).
edge(12,4).
edge(12,5).
edge(12,7).
edge(12,8).
edge(12,9).
edge(12,10).
edge(12,14).
edge(12,16).
edge(13,1).
edge(13,3).
edge(13,4).
edge(13,8).
edge(13,9).
edge(13,12).
edge(13,13).
edge(13,14).
edge(13,15).
edge(14,1).
edge(14,2).
edge(14,3).
edge(14,6).
edge(14,7).
edge(14,9).
edge(14,10).
edge(14,12).
edge(15,1).
edge(15,2).
edge(15,5).
edge(15,6).
edge(15,7).
edge(15,8).
edge(15,9).
edge(15,12).
edge(15,14).
edge(16,1).
edge(16,2).
edge(16,3).
edge(16,5).
edge(16,7).
edge(16,10).
edge(16,11).
edge(16,14).
edge(16,16).

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

