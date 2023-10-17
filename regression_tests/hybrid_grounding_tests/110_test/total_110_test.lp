a(1).

a(2) :- a(1).
a(3) :- a(2).


#program rules.
a(4) :- a(3).

b :- c(_).
c(X) :- a(X), X != 3.

