d(1).
c(1,2).
c(X,Y) :- a(X,Y).
c(X,X) :- d(X).

#program rules.
a(X,Y) :- c(Y,X).
