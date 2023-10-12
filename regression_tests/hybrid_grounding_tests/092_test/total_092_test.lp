e(1).
c(X) :- b(X).
b(X) :- a(X).
#program rules.
a(X) :- c(X).
b(X) :- e(X).
