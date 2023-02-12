

q(1,1).
q(1,2).
q(1,3).

b(1).

p(X,Y) :- b(X), q(X,Y).

h(X,Y) :- p(X,Y), 1 < #count{A,B : p(A,B)} < 4.

