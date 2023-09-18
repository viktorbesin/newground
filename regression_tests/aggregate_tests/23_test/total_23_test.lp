a1(1).
a2(2).

#program rules.
p(1) :- 3 <= #min{X1 : a1(X1), X1 = 1; X2 : a2(X2)} <= 4.

