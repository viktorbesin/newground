#program facts.
p(1).
p(5).

#program rules.
q(1) :- 1 <= #min{X : p(X)} <= 5.
