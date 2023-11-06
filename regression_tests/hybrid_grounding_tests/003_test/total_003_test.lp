#program facts.
p(1).
p(2).
p(6).

#program rules.

q(X,Y) :- p(X), p(Y), X = Y, X < 5.
