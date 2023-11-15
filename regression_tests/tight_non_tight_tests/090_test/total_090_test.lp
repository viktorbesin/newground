d(1).
e(1).

c(X) :- d(X), not e(X).

#program rules.

b(X) :- a(X).
c(X) :- b(X).
a(X) :- c(X).

