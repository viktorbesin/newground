d(1,1).
c(1,2).
c(X,Y) :- d(X,Y).
c(X,Y) :- a(X,Y).
#program rules.
a(X,Y) :- c(Y,X).

