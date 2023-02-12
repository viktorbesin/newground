b(1).
c(1,2).
r1_X(1) | r1_X(2).
r1_X(1) :- sat.
r1_X(2) :- sat.
r1_Y(1) | r1_Y(2).
r1_Y(1) :- sat.
r1_Y(2) :- sat.
r1_Z(1) | r1_Z(2).
r1_Z(1) :- sat.
r1_Z(2) :- sat.
sat_r1 :- r1_X(1), r1_Y(1), a(1,1).
sat_r1 :- r1_X(1), r1_Y(2), a(1,2).
sat_r1 :- r1_X(2), r1_Y(1), a(2,1).
sat_r1 :- r1_X(2), r1_Y(2), a(2,2).
sat_r1 :- r1_X(1), not b(1).
sat_r1 :- r1_X(2), not b(2).
sat_r1 :- r1_Y(1), r1_Z(1), not c(1,1).
sat_r1 :- r1_Y(1), r1_Z(2), not c(1,2).
sat_r1 :- r1_Y(2), r1_Z(1), not c(2,1).
sat_r1 :- r1_Y(2), r1_Z(2), not c(2,2).
{a(X,Y) : dom(X),dom(Y)}.
1<={r1f_Z(Z,1): dom(Z)}<=1 :- a(X,1), dom(X).
1<={r1f_Z(Z,2): dom(Z)}<=1 :- a(X,2), dom(X).
r1_unfound_0(1) :- not b(1).
r1_unfound_0(2) :- not b(2).
r1_unfound_1(1) :- not c(1,1), r1f_Z(1,1).
r1_unfound_1(1) :- not c(1,2), r1f_Z(2,1).
r1_unfound_1(2) :- not c(2,1), r1f_Z(1,2).
r1_unfound_1(2) :- not c(2,2), r1f_Z(2,2).
:- not sat.
sat :- sat_r1.
:- a(1,1), #sum {1:r1_unfound_1(1); 1:r1_unfound_0(1)} >= 1.
:- a(1,2), #sum {1:r1_unfound_1(2); 1:r1_unfound_0(1)} >= 1.
:- a(2,1), #sum {1:r1_unfound_1(1); 1:r1_unfound_0(2)} >= 1.
:- a(2,2), #sum {1:r1_unfound_1(2); 1:r1_unfound_0(2)} >= 1.
dom(1).
dom(2).
#show b/1.
#show c/2.
#show a/2.
#show dom/1.
