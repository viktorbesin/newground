xdom(1..400).
{ e(X,Y) } :- xdom(X),xdom(Y).
#program rules.
:- e(A,B), e(A,C), e(B,C), A < B, B < C.
