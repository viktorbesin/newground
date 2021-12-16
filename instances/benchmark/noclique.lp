%xdom(1..400).
{ f(X,Y) } :- e(X,Y). % xdom(X),xdom(Y).
#program rules.
:- f(A,B), f(A,C), f(B,C), A < B, B < C, A < C.
