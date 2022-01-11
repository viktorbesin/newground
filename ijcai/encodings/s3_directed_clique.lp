% guess used edge
{ f(X,Y) } :- edge(X,Y).

#program rules.
% has to contain at least 3-clique
c :- f(A,B), f(A,C), f(B,C), A != B, B != C, A != C.
:- not c.
