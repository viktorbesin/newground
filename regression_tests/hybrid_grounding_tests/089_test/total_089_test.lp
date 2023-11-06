c(1).
d(1).
b(X) :- a(X).
a(X) :- c(X), not d(X).

#program rules.

a(X) :- b(X).
