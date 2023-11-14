a(1).

a(2) :- a(1).
a(3) :- a(2).

b :- c(Y).

#program rules.
a(4) :- a(3).

c(X) :- a(X), X != 3.

