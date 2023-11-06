d(1).

#program rules.

a(X) :- d(X).
a(X) :- b(X).
a(X) :- c(X).

b(X) :- a(X).
c(X) :- a(X).

