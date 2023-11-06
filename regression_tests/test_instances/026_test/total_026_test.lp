a(1,2).
a(1,1).
a(2,1).
b(1,3).
p(1).
p(2).
o(3).

#program rules.
q(X) :- p(X), 3 <= #count{Y : a(X,Y); Z,1 : b(Z,H)}, o(H).



