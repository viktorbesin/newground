b(1).
c(1).
c(2).
d(1).

a(X) :- b(X).

#program rules.

e(X) :- c(X), not d(X).
