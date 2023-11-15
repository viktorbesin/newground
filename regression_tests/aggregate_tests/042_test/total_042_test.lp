p(1).
p(2).
p(3).
a(4).

#program rules.
:- a(Z), #count{X : p(X)} = Z.

