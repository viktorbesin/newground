a(1).
b(1).


a(X) :- c(X).
#program rules.
c(X) :- a(X), not b(X).

d(X) :- c(X).
e(X) :- d(X).
d(X) :- e(X).

f(X) :- e(X).
g(X) :- f(X).
f(X) :- g(X).

a(X) :- g(X).


