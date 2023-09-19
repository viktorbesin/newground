a(1,2).
a(1,1).
a(2,1).
p(1).
p(2).

#program rules.
q(X) :- p(X), 2 <= #min{Y : a(X,Y)}.



