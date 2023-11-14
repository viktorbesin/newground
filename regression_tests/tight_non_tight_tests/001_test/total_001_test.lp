#program facts.
p(1,1).
p(2,2).

#program rules.
q(A,B) :- p(X,Y), p(A,B).


