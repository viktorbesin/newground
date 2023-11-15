a(1,2,3).

#program rules.

b :- a(_,X,3).
d :- a(_,X,4).

c(X) :- a(_,X,_).
e(X) :- a(_,_,X).

f(X,Y,1) :- c(X), e(Y), b, not d.




