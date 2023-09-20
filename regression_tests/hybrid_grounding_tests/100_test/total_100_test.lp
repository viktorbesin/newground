b(1).
c(1).

a(X) :- b(X), not c(X).
#program rules.
a(X) :- b(X), not c(X).

a(X) :- c(X).
c(X) :- a(X).


