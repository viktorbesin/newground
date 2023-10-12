b(1).
b(X) :- a(X).

#program rules.

a(X) :- c(X), not d(X).
a(X) :- b(X).
