#program facts.
b(1).
c(1,2).


#program rules.
a(X,Y) :- b(X), c(Y,Z).

d :- not e.
e :- not d.
