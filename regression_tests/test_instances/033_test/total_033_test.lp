b(1).
c(1).
c(2).
d(1).
g(X) :- a(X).
h(X) :- g(X).
a(X) :- f(X).


#program rules.

f(X) :- h(X).
a(X) :- c(X), not d(X).



