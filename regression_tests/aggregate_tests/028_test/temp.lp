#show b/2.
#show c/1.
#show q/1.
#show a/2.
#show p/1.
p(1).
p(2).
a(1,2).
a(1,3).
b(1,2).
b(2,1).
c(1).
c(2).
#program rules.
#program max.
max_ag0_left_0(X) :- a(X,Y_0),Y_0 >= 2.
#program max.
max_ag0_left_1(H) :- b(Z_1,H),Z_1 >= 2.
not_max_ag0_left(X,H) :- p(X),c(H),not max_ag0_left_0(X),not max_ag0_left_1(H).
q(X) :- p(X),c(H),not not_max_ag0_left(X,H).
#program rules.

