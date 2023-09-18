
b(1).

a(X) :- b(X).

#program rules.

c(X) :- a(X).
a(X) :- c(X).
b(X) :- a(X).

