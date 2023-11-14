#program facts.
p(1,1).
p(2,1).

#program rules.
q(X,1) :- p(X,1), p(Y,1), X = Y, p(A,B).
q(X,2) :- p(X,1), p(Y,1), X = Y.

