c(1).
d(1).

b(X) :- c(X), not d(X).

#program rules.

a(X) :- b(X).
b(X) :- a(X).
