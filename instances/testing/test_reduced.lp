r1_X(1), r1_X(2).
r1_X(1) :- sat.
r1_X(2) :- sat.
r1_Z(1), r1_Z(2).
r1_Z(1) :- sat.
r1_Z(2) :- sat.
r1_Y(1), r1_Y(2).
r1_Y(1) :- sat.
r1_Y(2) :- sat.
sat_r1 :- r1_X(1), r1_Z(1), r1_Y(1),  p(1,1).
sat_r1 :- r1_X(1), r1_Z(1), r1_Y(1), b(V1,V2), V1 != 1, V2 != 1.
sat_r1 :- r1_X(1), r1_Z(1), r1_Y(1), c(V1,V2), V1 != 1, V2 != 1.
sat_r1 :- r1_X(1), r1_Z(1), r1_Y(2),  p(1,1).
sat_r1 :- r1_X(1), r1_Z(1), r1_Y(2), b(V1,V2), V1 != 1, V2 != 2.
sat_r1 :- r1_X(1), r1_Z(1), r1_Y(2), c(V1,V2), V1 != 2, V2 != 1.
sat_r1 :- r1_X(1), r1_Z(2), r1_Y(1),  p(1,2).
sat_r1 :- r1_X(1), r1_Z(2), r1_Y(1), b(V1,V2), V1 != 1, V2 != 1.
sat_r1 :- r1_X(1), r1_Z(2), r1_Y(1), c(V1,V2), V1 != 1, V2 != 2.
sat_r1 :- r1_X(1), r1_Z(2), r1_Y(2),  p(1,2).
sat_r1 :- r1_X(1), r1_Z(2), r1_Y(2), not b(1,2).
sat_r1 :- r1_X(1), r1_Z(2), r1_Y(2), not c(2,2).
sat_r1 :- r1_X(2), r1_Z(1), r1_Y(1),  p(2,1).
sat_r1 :- r1_X(2), r1_Z(1), r1_Y(1), not b(2,1).
sat_r1 :- r1_X(2), r1_Z(1), r1_Y(1), not c(1,1).
sat_r1 :- r1_X(2), r1_Z(1), r1_Y(2),  p(2,1).
sat_r1 :- r1_X(2), r1_Z(1), r1_Y(2), not b(2,2).
sat_r1 :- r1_X(2), r1_Z(1), r1_Y(2), not c(2,1).
sat_r1 :- r1_X(2), r1_Z(2), r1_Y(1),  p(2,2).
sat_r1 :- r1_X(2), r1_Z(2), r1_Y(1), not b(2,1).
sat_r1 :- r1_X(2), r1_Z(2), r1_Y(1), not c(1,2).
sat_r1 :- r1_X(2), r1_Z(2), r1_Y(2),  p(2,2).
sat_r1 :- r1_X(2), r1_Z(2), r1_Y(2), not b(2,2).
sat_r1 :- r1_X(2), r1_Z(2), r1_Y(2), not c(2,2).
sat :- sat_r1.

1{r1_Y_f(D) : dom(D)}1 :- p(X,Z).

r1_p_f(X,Z) :- b(X,Y),c(Y,Z), r1_Y_f(Y).
:- not r1_p_f(X,Z), p(X,Z).

{p(D0,D1) : dom(D0),dom(D1)}.

dom((1..2)).
b(1,2).
c(2,1).
b(1,1).
c(1,2).
c(1,1).
:- not sat.
#show p/2.
#show b/2.
#show c/2.
#show dom/1.
