b(1).
c(1).
c(2).
d(1).

a(X) :- b(X).

#program rules.

a(X) :- c(X), not d(X).
