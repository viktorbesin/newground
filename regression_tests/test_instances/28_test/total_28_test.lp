p(1).
p(2).

a(1,2).
a(2,1).

b(1,2).
b(2,1).

c(1).
c(2).

#program rules.
q(X) :- p(X), c(H), 2 <= #max{Y : a(X,Y); Z : b(Z,H)}.
