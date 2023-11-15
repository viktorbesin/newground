#program facts.
p(1).
p(5).

#program rules.
q(1) :- 1 <= #max{X : p(X)} <= 5.

