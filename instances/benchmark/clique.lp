xdom(1..400).
{ f(X,Y) } :- xdom(X),xdom(Y).
:- not c.
#program rules.
c :- f(A,B), f(A,C), f(B,C), A < B, B < C, A < C.
