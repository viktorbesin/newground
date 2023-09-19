

a(1).

#program rules.
b(X) :- a(X).

c(X) :- b(X).
d(X) :- c(X).
b(X) :- d(X).
