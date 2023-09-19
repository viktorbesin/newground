d(1,1).
c(1,2).
c(X,Y) :- d(X,Y).
0 <= {c3(X,Y)} <= 1 :- a(X,Y).
c(X,Y) :- c3(X,Y).
:- a(X,Y), not c(X,Y).
r3_unfound(2,1) :- not prec(a(2,1),c3(2,1)).
r3_3_unfound(2,1) :- not prec(c3(2,1),c(2,1)).
r3_unfound(2,2) :- not prec(a(2,2),c3(2,2)).
r3_3_unfound(2,2) :- not prec(c3(2,2),c(2,2)).
r3_unfound(1,1) :- not prec(a(1,1),c3(1,1)).
r3_3_unfound(1,1) :- not prec(c3(1,1),c(1,1)).
r3_unfound(1,2) :- not prec(a(1,2),c3(1,2)).
r3_3_unfound(1,2) :- not prec(c3(1,2),c(1,2)).
r4_X(2) | r4_X(1).
r4_X(2) :- sat.
r4_X(1) :- sat.
r4_Y(1) | r4_Y(2).
r4_Y(1) :- sat.
r4_Y(2) :- sat.
sat_r4 :- r4_X(2),r4_Y(1),a(2,1).
sat_r4 :- r4_X(2),r4_Y(2),a(2,2).
sat_r4 :- r4_X(1),r4_Y(1),a(1,1).
sat_r4 :- r4_X(1),r4_Y(2),a(1,2).
sat_r4 :- r4_Y(1),r4_X(2),not c(1,2).
sat_r4 :- r4_Y(1),r4_X(1),not c(1,1).
sat_r4 :- r4_Y(2),r4_X(2),not c(2,2).
sat_r4 :- r4_Y(2),r4_X(1),not c(2,1).
domain_rule_4_variable_X(2).
domain_rule_4_variable_X(1).
domain_rule_4_variable_Y(1).
domain_rule_4_variable_Y(2).
{a4(X,Y) : domain_rule_4_variable_X(X),domain_rule_4_variable_Y(Y)} .
a(X,Y) :- a4(X,Y).
r4_unfound(1,2) :- not c(2,1).
r4_unfound(1,2) :- not prec(c(2,1),a4(1,2)).
r4_4_unfound(1,2) :- not prec(a4(1,2),a(1,2)).
r4_unfound(1,1) :- not c(1,1).
r4_unfound(1,1) :- not prec(c(1,1),a4(1,1)).
r4_4_unfound(1,1) :- not prec(a4(1,1),a(1,1)).
r4_unfound(2,2) :- not c(2,2).
r4_unfound(2,2) :- not prec(c(2,2),a4(2,2)).
r4_4_unfound(2,2) :- not prec(a4(2,2),a(2,2)).
r4_unfound(2,1) :- not c(1,2).
r4_unfound(2,1) :- not prec(c(1,2),a4(2,1)).
r4_4_unfound(2,1) :- not prec(a4(2,1),a(2,1)).
1 <= {prec(c(Y_1,X_1),a(X_2,Y_2));prec(a(X_2,Y_2),c(Y_1,X_1))} <= 1 :- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2).
1 <= {prec(c(Y_1,X_1),c3(X_2,Y_2));prec(c3(X_2,Y_2),c(Y_1,X_1))} <= 1 :- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2).
1 <= {prec(c(Y_1,X_1),a4(X_2,Y_2));prec(a4(X_2,Y_2),c(Y_1,X_1))} <= 1 :- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2).
1 <= {prec(a(X_1,Y_1),c3(X_2,Y_2));prec(c3(X_2,Y_2),a(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(a(X_1,Y_1),a4(X_2,Y_2));prec(a4(X_2,Y_2),a(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c3(X_1,Y_1),a4(X_2,Y_2));prec(a4(X_2,Y_2),c3(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
:- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(Y_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,Y_3)), prec(c3(X_3,Y_3),c(Y_1,X_1)).
:- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(Y_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a4(X_3,Y_3)), prec(a4(X_3,Y_3),c(Y_1,X_1)).
:- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(Y_1,X_1),c3(X_2,Y_2)), prec(c3(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(Y_1,X_1)).
:- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(Y_1,X_1),c3(X_2,Y_2)), prec(c3(X_2,Y_2),a4(X_3,Y_3)), prec(a4(X_3,Y_3),c(Y_1,X_1)).
:- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(Y_1,X_1),a4(X_2,Y_2)), prec(a4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(Y_1,X_1)).
:- dom(Y_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(Y_1,X_1),a4(X_2,Y_2)), prec(a4(X_2,Y_2),c3(X_3,Y_3)), prec(c3(X_3,Y_3),c(Y_1,X_1)).
:- dom(X_1),dom(Y_1), dom(Y_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c(Y_2,X_2)), prec(c(Y_2,X_2),c3(X_3,Y_3)), prec(c3(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(Y_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c(Y_2,X_2)), prec(c(Y_2,X_2),a4(X_3,Y_3)), prec(a4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(Y_3),dom(X_3), prec(a(X_1,Y_1),c3(X_2,Y_2)), prec(c3(X_2,Y_2),c(Y_3,X_3)), prec(c(Y_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c3(X_2,Y_2)), prec(c3(X_2,Y_2),a4(X_3,Y_3)), prec(a4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(Y_3),dom(X_3), prec(a(X_1,Y_1),a4(X_2,Y_2)), prec(a4(X_2,Y_2),c(Y_3,X_3)), prec(c(Y_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),a4(X_2,Y_2)), prec(a4(X_2,Y_2),c3(X_3,Y_3)), prec(c3(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(Y_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,Y_1),c(Y_2,X_2)), prec(c(Y_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(Y_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,Y_1),c(Y_2,X_2)), prec(c(Y_2,X_2),a4(X_3,Y_3)), prec(a4(X_3,Y_3),c3(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(Y_3),dom(X_3), prec(c3(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(Y_3,X_3)), prec(c(Y_3,X_3),c3(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a4(X_3,Y_3)), prec(a4(X_3,Y_3),c3(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(Y_3),dom(X_3), prec(c3(X_1,Y_1),a4(X_2,Y_2)), prec(a4(X_2,Y_2),c(Y_3,X_3)), prec(c(Y_3,X_3),c3(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,Y_1),a4(X_2,Y_2)), prec(a4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(Y_2),dom(X_2), dom(X_3),dom(Y_3), prec(a4(X_1,Y_1),c(Y_2,X_2)), prec(c(Y_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(Y_2),dom(X_2), dom(X_3),dom(Y_3), prec(a4(X_1,Y_1),c(Y_2,X_2)), prec(c(Y_2,X_2),c3(X_3,Y_3)), prec(c3(X_3,Y_3),a4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(Y_3),dom(X_3), prec(a4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(Y_3,X_3)), prec(c(Y_3,X_3),a4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,Y_3)), prec(c3(X_3,Y_3),a4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(Y_3),dom(X_3), prec(a4(X_1,Y_1),c3(X_2,Y_2)), prec(c3(X_2,Y_2),c(Y_3,X_3)), prec(c(Y_3,X_3),a4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a4(X_1,Y_1),c3(X_2,Y_2)), prec(c3(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a4(X_1,Y_1)).
:- not sat.
sat :- sat_r4.
:- r4_4_unfound(1,1), a4(1,1).
:- r4_4_unfound(1,2), a4(1,2).
:- r3_3_unfound(2,1), c3(2,1).
:- r4_4_unfound(2,1), a4(2,1).
:- r3_3_unfound(1,1), c3(1,1).
:- r3_3_unfound(1,2), c3(1,2).
:- r3_3_unfound(2,2), c3(2,2).
:- r4_4_unfound(2,2), a4(2,2).
:- c3(2,1), #sum{1,0 : r3_unfound(2,1)} >=1 .
:- c3(2,2), #sum{1,0 : r3_unfound(2,2)} >=1 .
:- c3(1,1), #sum{1,0 : r3_unfound(1,1)} >=1 .
:- c3(1,2), #sum{1,0 : r3_unfound(1,2)} >=1 .
:- a4(1,2), #sum{1,0 : r4_unfound(1,2)} >=1 .
:- a4(1,1), #sum{1,0 : r4_unfound(1,1)} >=1 .
:- a4(2,2), #sum{1,0 : r4_unfound(2,2)} >=1 .
:- a4(2,1), #sum{1,0 : r4_unfound(2,1)} >=1 .
dom(1).
dom(2).
#show d/2.
#show c/2.
#show a/2.
