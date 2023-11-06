#program facts.
p(1).
q(1).
p(2).
q(3).

a(5).

#program rules.
a(X) :- p(X), q(X).
b(X) :- a(X).
