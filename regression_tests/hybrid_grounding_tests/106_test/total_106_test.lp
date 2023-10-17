a(1).
b(2) :- a(1).
b(1) :- a(2).

#program rules.
a(X) :- b(X).

