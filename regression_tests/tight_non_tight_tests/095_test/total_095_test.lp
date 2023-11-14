d(1,2).
d(2,3).
d(3,4).
d(2,1).

#program rules.
c(X,Y,X) :- d(X,Y).

