#program facts.
p(1).
p(2).

#program rules.
q(X) :- p(X), 1 = X.
k(X) :- p(X), 2 = X.
