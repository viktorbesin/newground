a1(1).
a2(2).

#program rules.
p(1) :- 1 <= #max{X1 : a1(X1), X1 = 1; X2 : a2(X2)} <= 2.

