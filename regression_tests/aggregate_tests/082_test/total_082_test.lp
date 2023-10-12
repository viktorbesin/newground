p(1,1).
p(2,2).
p(3,3).
p(3,4).

a(1).
a(2).
a(3).
a(4).

#program rules.
l(Z) :- a(Z), Z = #sum{X : p(X,Z)}.

