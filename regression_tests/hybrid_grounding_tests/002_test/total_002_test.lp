#program facts.
p(1).
p(2).
p(3).

#program rules.

a(1) :- not a(2).
a(2) :- not a(1).

q(X) :- p(X), p(Y), X = Y.
