p(1).
q(1).
q(2).
k(1).
k(2).
k(3).

a(6).

#program rules.
:- a(Z), Z >= #sum{X : p(X); X : q(X); X,Y : p(X),k(Y)}.

