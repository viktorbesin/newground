a(1).
b(1).

#program rules.


c(X) :- a(X), not b(X).
d(X) :- c(X).
c(X) :- d(X).

e(X) :- c(X).

f(X) :- e(X).
e(X) :- f(X).

