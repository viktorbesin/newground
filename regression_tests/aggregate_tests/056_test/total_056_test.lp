p(1).
p(2).
p(3).
q(4).
q(5).
q(2).

a(1).

#program rules.
:- a(Z), #max{X : p(X); X : q(X); X,Y : p(X),q(Y)} > Z.

