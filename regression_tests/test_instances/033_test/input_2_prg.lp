e(1).
c(1) :- b(1).
b(1) :- a(1).
#program rules.
a(X) :- c(X).
b(X) :- e(X).
