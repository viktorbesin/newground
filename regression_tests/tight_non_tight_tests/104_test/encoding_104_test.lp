
c(X) :- a(X), not b(X).
a(X) :- c(X).

d(X) :- a(X).
e(X) :- d(X).
d(X) :- e(X).

