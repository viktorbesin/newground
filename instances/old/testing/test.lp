#program facts.
b(1,2).
c(2,1).

b(1,1).
c(1,2).
c(1,1).

#program rules.
p(X,Y) :- b(X,Y), c(Y,Z).
