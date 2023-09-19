#program facts.
p(1).
p(2).

#program rules.
q(X,1) :- p(X), p(Y), X = Y.
q(X,2) :- p(X), p(Y), X = Y.

