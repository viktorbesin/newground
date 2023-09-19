#program facts.
p(1).
p(2).

#program rules.
q(X) :- p(X), not p(1).
