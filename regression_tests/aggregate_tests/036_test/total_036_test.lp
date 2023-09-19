p(1).
p(2).
p(3).
a(3).

#program rules.
:- a(Z), 1 < #count{X : p(X)} < Z.
