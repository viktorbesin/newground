b(1).
c(1).
c(2).
d(1).

a(X) :- b(X).
c(X) :- a(X).
d(X) :- c(X).
a(X) :- d(X).

g(X) :- a(X).
h(X) :- g(X).
a(X) :- h(X).

y(X) :- z(X).

#program rules.

a(X) :- c(X), not d(X).

z(X) :- y(X).



