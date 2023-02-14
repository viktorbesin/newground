
p(1).

p(X + 1) :- p(X), l(X), X < 3.

q(X,1,1) :- p(X).
q(X,Y,Z1 + 1) :- q(X,Y,Z1), Z1 < 3.
q(X,Y+1,Z) :- q(X,Y,Z), Y < 3.

l(X) :- p(X), 0 < #count{A,B:q(X,A,B)} <= 10 + X.

