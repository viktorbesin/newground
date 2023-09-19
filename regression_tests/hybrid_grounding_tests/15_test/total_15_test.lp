#program facts.
p(1).
p(2).

#program rules.
q(X,Y) :- p(X), p(Y), X = Y.
q(X,Y) :- p(X), p(Y), X != Y.








