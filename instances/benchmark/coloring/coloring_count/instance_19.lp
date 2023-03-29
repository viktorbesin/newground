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
vertex(17).
vertex(18).
edge(1,6).
edge(1,7).
edge(1,8).
edge(1,11).
edge(1,12).
edge(1,13).
edge(1,17).
edge(2,1).
edge(2,3).
edge(2,5).
edge(2,6).
edge(2,8).
edge(2,9).
edge(2,11).
edge(2,14).
edge(2,16).
edge(2,17).
edge(3,2).
edge(3,4).
edge(3,6).
edge(3,8).
edge(3,10).
edge(3,11).
edge(3,12).
edge(3,13).
edge(3,15).
edge(3,17).
edge(3,18).
edge(4,1).
edge(4,2).
edge(4,3).
edge(4,4).
edge(4,5).
edge(4,6).
edge(4,10).
edge(4,11).
edge(4,14).
edge(4,15).
edge(4,16).
edge(4,17).
edge(5,1).
edge(5,2).
edge(5,3).
edge(5,5).
edge(5,7).
edge(5,8).
edge(5,10).
edge(5,11).
edge(6,1).
edge(6,3).
edge(6,5).
edge(6,6).
edge(6,7).
edge(6,9).
edge(6,11).
edge(6,12).
edge(6,13).
edge(6,14).
edge(6,17).
edge(7,1).
edge(7,2).
edge(7,4).
edge(7,6).
edge(7,8).
edge(7,11).
edge(7,15).
edge(7,17).
edge(8,3).
edge(8,4).
edge(8,5).
edge(8,6).
edge(8,7).
edge(8,9).
edge(8,11).
edge(8,12).
edge(8,16).
edge(8,18).
edge(9,1).
edge(9,5).
edge(9,6).
edge(9,7).
edge(9,8).
edge(9,10).
edge(9,13).
edge(9,16).
edge(10,1).
edge(10,3).
edge(10,4).
edge(10,5).
edge(10,7).
edge(10,8).
edge(10,10).
edge(10,12).
edge(10,15).
edge(10,16).
edge(10,17).
edge(10,18).
edge(11,1).
edge(11,2).
edge(11,4).
edge(11,5).
edge(11,6).
edge(11,8).
edge(11,9).
edge(11,11).
edge(11,12).
edge(11,15).
edge(11,16).
edge(11,17).
edge(11,18).
edge(12,1).
edge(12,2).
edge(12,3).
edge(12,4).
edge(12,5).
edge(12,7).
edge(12,10).
edge(12,11).
edge(12,16).
edge(13,2).
edge(13,3).
edge(13,4).
edge(13,5).
edge(13,7).
edge(13,11).
edge(13,16).
edge(14,1).
edge(14,2).
edge(14,3).
edge(14,4).
edge(14,5).
edge(14,6).
edge(14,9).
edge(14,10).
edge(14,13).
edge(14,18).
edge(15,2).
edge(15,4).
edge(15,5).
edge(15,6).
edge(15,11).
edge(15,12).
edge(15,13).
edge(15,14).
edge(15,16).
edge(16,1).
edge(16,3).
edge(16,4).
edge(16,5).
edge(16,8).
edge(16,10).
edge(16,11).
edge(16,12).
edge(16,13).
edge(16,14).
edge(16,15).
edge(16,17).
edge(17,4).
edge(17,5).
edge(17,8).
edge(17,10).
edge(17,11).
edge(17,13).
edge(17,15).
edge(17,16).
edge(17,18).
edge(18,1).
edge(18,3).
edge(18,5).
edge(18,8).
edge(18,13).
edge(18,16).
edge(18,17).

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



violation(X,Y) :- edge(X,Y), g(X), g(Y).
violation(X,Y) :- edge(X,Y), b(X), b(Y).
violation(X,Y) :- edge(X,Y), r(X), r(Y).

violation_2(Y2,X2) :- violation(X,Y), X2 = 2 * X, Y2 = 2 * Y.
violation_3(X3,Y3) :- violation(X,Y), X3 = 4 * X, Y3 = 4 * Y.


