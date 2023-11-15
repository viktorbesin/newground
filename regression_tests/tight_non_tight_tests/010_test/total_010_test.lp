#program facts.
p(1,5).
p(2,6).

l(3).
l(4).

#program rules.
k(X,Y) :- q(X,Y).

q(X,Y) :- p(X,Y).
m(X) :- l(X).





