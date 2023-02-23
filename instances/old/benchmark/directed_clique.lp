{ f(X,Y) } :- edge(X,Y). %xdom(X),xdom(Y).

#program rules.
:- not c.
c :- f(A,B), f(A,C), f(B,C), A != B, B != C, A != C.
