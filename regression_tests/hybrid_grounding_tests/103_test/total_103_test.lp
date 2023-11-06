d(1).
c(1,2).
c(X,X) :- d(X).
c(X,Y) :- a(X,Y).
#program rules.
a(X,Y) :- c(Y,X).
