b(1,2).
c(2,1).
b(1,1).
c(1,2).
c(1,1).
r1_X(1), r1_X(2).
r1_X(1) :- sat.
r1_X(2) :- sat.
r1_Y(1), r1_Y(2).
r1_Y(1) :- sat.
r1_Y(2) :- sat.
r1_Z(1), r1_Z(2).
r1_Z(1) :- sat.
r1_Z(2) :- sat.
sat_r1 :- r1_X(1), r1_Y(1),  p(1,1).
sat_r1 :- r1_X(1), r1_Y(2),  p(1,2).
sat_r1 :- r1_X(2), r1_Y(1),  p(2,1).
sat_r1 :- r1_X(2), r1_Y(2),  p(2,2).
sat_r1 :- r1_X(1), r1_Y(1), not b(1,1).
sat_r1 :- r1_X(1), r1_Y(2), not b(1,2).
sat_r1 :- r1_X(2), r1_Y(1), not b(2,1).
sat_r1 :- r1_X(2), r1_Y(2), not b(2,2).
sat_r1 :- r1_Y(1), r1_Z(1), not c(1,1).
sat_r1 :- r1_Y(1), r1_Z(2), not c(1,2).
sat_r1 :- r1_Y(2), r1_Z(1), not c(2,1).
sat_r1 :- r1_Y(2), r1_Z(2), not c(2,2).
{p(X,Y) : dom(X),dom(Y)}.
r1_unfound(1,1) :- not b(1,1).
r1_unfound(1,2) :- not b(1,2).
r1_unfound(2,1) :- not b(2,1).
r1_unfound(2,2) :- not b(2,2).
1{r1_Z(Z,1,1): dom(Z)}1 :- p(1,1).
r1_unfound(1,1) :- not c(1,1), r1_Z(1,1,1).
r1_unfound(1,1) :- not c(1,2), r1_Z(2,1,1).
1{r1_Z(Z,1,2): dom(Z)}1 :- p(1,2).
r1_unfound(1,2) :- not c(2,1), r1_Z(1,1,2).
r1_unfound(1,2) :- not c(2,2), r1_Z(2,1,2).
1{r1_Z(Z,2,1): dom(Z)}1 :- p(2,1).
r1_unfound(2,1) :- not c(1,1), r1_Z(1,2,1).
r1_unfound(2,1) :- not c(1,2), r1_Z(2,2,1).
1{r1_Z(Z,2,2): dom(Z)}1 :- p(2,2).
r1_unfound(2,2) :- not c(2,1), r1_Z(1,2,2).
r1_unfound(2,2) :- not c(2,2), r1_Z(2,2,2).
:- not sat.
sat :- sat_r1.
:- p(1,1), r1_unfound(1,1).
:- p(1,2), r1_unfound(1,2).
:- p(2,1), r1_unfound(2,1).
:- p(2,2), r1_unfound(2,2).
dom(1).
dom(2).
#show p/2.
#show b/2.
#show c/2.
