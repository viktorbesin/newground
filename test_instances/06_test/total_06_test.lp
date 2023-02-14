#program facts.
xdom(1..3).
{ f(X,Y)}  :- xdom(X),xdom(Y).

#program rules.

:- f(A,B), f(A,C), f(B,C), A < B, B < C.
