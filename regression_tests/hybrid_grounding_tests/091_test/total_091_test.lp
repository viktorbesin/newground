d(1).
e(1).

c(X) :- d(X), not e(X).
c(X) :- b(X).

#program rules.

b(X) :- a(X).
a(X) :- c(X).

