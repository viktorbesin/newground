%xdom(1..400).
{ f(X,Y) } :- e(X,Y). %xdom(X),xdom(Y).
:- not c.
#program rules.
c :- f(A,B), f(A,C), f(B,C), f(A,D), f(B,D), f(C,D), A < B, B < C, C < D, A < C, B < D, A < D.
