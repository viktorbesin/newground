e(1).
c(1,2).
d(X,X) :- e(X).
c(X,X) :- d(X,Y).
c(X,Y) :- a(X,Y).
#program rules.
a(X,Y) :- c(Y,X).
d(X,X) :- a(X,Y).
c(X,Y) :- d(X,Y).
