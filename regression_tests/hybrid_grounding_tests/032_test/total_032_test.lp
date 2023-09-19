c(1).
d(1).

#program rules.

a(X) :- c(X), not d(X).
a(X) :- b(X).
b(X) :- a(X).
