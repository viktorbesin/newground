b(1).

a(X) :- b(X).

#program rules.

a(X) :- c(X), not d(X).
b(X) :- a(X).
