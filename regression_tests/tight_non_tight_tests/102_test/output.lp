c(1,2).
c(X,X) :- d(X,Y).
c(X,Y) :- a(X,Y).
c(X,Y) :- d(X,Y).
d(X,X) :- e(X).
d(X,X) :- a(X,Y).
a(X,Y) :- c(Y,X).
e(1).
c(1,2).
d(X,X) :- e(X).
0 <= {c3(X,X)} <= 1 :- d(X,Y).
c(X,X) :- c3(X,X).
:- d(X,Y), not c(X,X).
domain_rule_3_variable_Y(1).
domain_rule_3_variable_Y(2).
1<={r3f_Y(Y,1,1):domain_rule_3_variable_Y(Y)}<=1 :- c3(1,1).
1<={r3f_Y(Y,2,2):domain_rule_3_variable_Y(Y)}<=1 :- c3(2,2).
r3_unfound(1,1) :- r3f_Y(1,1,1), not prec(d(1,1),c3(1,1)).
r3_3_unfound(1,1) :- r3f_Y(1,1,1), not prec(c3(1,1),c(1,1)).
r3_unfound(2,2) :- r3f_Y(2,2,2), not prec(d(2,2),c3(2,2)).
r3_3_unfound(2,2) :- r3f_Y(2,2,2), not prec(c3(2,2),c(2,2)).
0 <= {c4(X,Y)} <= 1 :- a(X,Y).
c(X,Y) :- c4(X,Y).
:- a(X,Y), not c(X,Y).
r4_unfound(1,1) :- not prec(a(1,1),c4(1,1)).
r4_4_unfound(1,1) :- not prec(c4(1,1),c(1,1)).
r4_unfound(1,2) :- not prec(a(1,2),c4(1,2)).
r4_4_unfound(1,2) :- not prec(c4(1,2),c(1,2)).
r4_unfound(2,1) :- not prec(a(2,1),c4(2,1)).
r4_4_unfound(2,1) :- not prec(c4(2,1),c(2,1)).
r4_unfound(2,2) :- not prec(a(2,2),c4(2,2)).
r4_4_unfound(2,2) :- not prec(c4(2,2),c(2,2)).
r5_X(1) | r5_X(2).
r5_X(1) :- sat.
r5_X(2) :- sat.
r5_Y(1) | r5_Y(2).
r5_Y(1) :- sat.
r5_Y(2) :- sat.
sat_r5 :- r5_X(1),r5_Y(1),a(1,1).
sat_r5 :- r5_Y(2),r5_X(1),a(1,2).
sat_r5 :- r5_X(2),r5_Y(1),a(2,1).
sat_r5 :- r5_X(2),r5_Y(2),a(2,2).
sat_r5 :- r5_X(1),r5_Y(1),not c(1,1).
sat_r5 :- r5_X(2),r5_Y(1),not c(1,2).
sat_r5 :- r5_X(1),r5_Y(2),not c(2,1).
sat_r5 :- r5_X(2),r5_Y(2),not c(2,2).
domain_rule_5_variable_X(1).
domain_rule_5_variable_X(2).
domain_rule_5_variable_Y(1).
domain_rule_5_variable_Y(2).
{a5(X,Y) : domain_rule_5_variable_X(X),domain_rule_5_variable_Y(Y)} .
a(X,Y) :- a5(X,Y).
r5_unfound(1,1) :- not c(1,1).
r5_unfound(1,1) :- not prec(c(1,1),a5(1,1)).
r5_5_unfound(1,1) :- not prec(a5(1,1),a(1,1)).
r5_unfound(2,1) :- not c(1,2).
r5_unfound(2,1) :- not prec(c(1,2),a5(2,1)).
r5_5_unfound(2,1) :- not prec(a5(2,1),a(2,1)).
r5_unfound(1,2) :- not c(2,1).
r5_unfound(1,2) :- not prec(c(2,1),a5(1,2)).
r5_5_unfound(1,2) :- not prec(a5(1,2),a(1,2)).
r5_unfound(2,2) :- not c(2,2).
r5_unfound(2,2) :- not prec(c(2,2),a5(2,2)).
r5_5_unfound(2,2) :- not prec(a5(2,2),a(2,2)).
r6_X(1) | r6_X(2).
r6_X(1) :- sat.
r6_X(2) :- sat.
r6_Y(1) | r6_Y(2).
r6_Y(1) :- sat.
r6_Y(2) :- sat.
sat_r6 :- r6_X(1),d(1,1).
sat_r6 :- r6_X(2),d(2,2).
sat_r6 :- r6_Y(1),r6_X(1),not a(1,1).
sat_r6 :- r6_X(1),r6_Y(2),not a(1,2).
sat_r6 :- r6_Y(1),r6_X(2),not a(2,1).
sat_r6 :- r6_X(2),r6_Y(2),not a(2,2).
domain_rule_6_variable_X(1).
domain_rule_6_variable_X(2).
{d6(X,X) : domain_rule_6_variable_X(X)} .
d(X,X) :- d6(X,X).
domain_rule_6_variable_Y(1).
domain_rule_6_variable_Y(2).
1<={r6f_Y(Y,1,1):domain_rule_6_variable_Y(Y)}<=1 :- d6(1,1).
1<={r6f_Y(Y,2,2):domain_rule_6_variable_Y(Y)}<=1 :- d6(2,2).
r6_unfound(1,1) :- r6f_Y(1,1,1), not a(1,1).
r6_unfound(1,1) :- r6f_Y(1,1,1), not prec(a(1,1),d6(1,1)).
r6_6_unfound(1,1) :- r6f_Y(1,1,1), not prec(d6(1,1),d(1,1)).
r6_unfound(2,2) :- r6f_Y(2,2,2), not a(2,2).
r6_unfound(2,2) :- r6f_Y(2,2,2), not prec(a(2,2),d6(2,2)).
r6_6_unfound(2,2) :- r6f_Y(2,2,2), not prec(d6(2,2),d(2,2)).
r7_X(1) | r7_X(2).
r7_X(1) :- sat.
r7_X(2) :- sat.
r7_Y(1) | r7_Y(2).
r7_Y(1) :- sat.
r7_Y(2) :- sat.
sat_r7 :- r7_Y(1),r7_X(1),c(1,1).
sat_r7 :- r7_X(1),r7_Y(2),c(1,2).
sat_r7 :- r7_Y(1),r7_X(2),c(2,1).
sat_r7 :- r7_X(2),r7_Y(2),c(2,2).
sat_r7 :- r7_Y(1),r7_X(1),not d(1,1).
sat_r7 :- r7_X(1),r7_Y(2),not d(1,2).
sat_r7 :- r7_Y(1),r7_X(2),not d(2,1).
sat_r7 :- r7_X(2),r7_Y(2),not d(2,2).
domain_rule_7_variable_X(1).
domain_rule_7_variable_X(2).
domain_rule_7_variable_Y(1).
domain_rule_7_variable_Y(2).
{c7(X,Y) : domain_rule_7_variable_X(X),domain_rule_7_variable_Y(Y)} .
c(X,Y) :- c7(X,Y).
r7_unfound(1,1) :- not d(1,1).
r7_unfound(1,1) :- not prec(d(1,1),c7(1,1)).
r7_7_unfound(1,1) :- not prec(c7(1,1),c(1,1)).
r7_unfound(1,2) :- not d(1,2).
r7_unfound(1,2) :- not prec(d(1,2),c7(1,2)).
r7_7_unfound(1,2) :- not prec(c7(1,2),c(1,2)).
r7_unfound(2,1) :- not d(2,1).
r7_unfound(2,1) :- not prec(d(2,1),c7(2,1)).
r7_7_unfound(2,1) :- not prec(c7(2,1),c(2,1)).
r7_unfound(2,2) :- not d(2,2).
r7_unfound(2,2) :- not prec(d(2,2),c7(2,2)).
r7_7_unfound(2,2) :- not prec(c7(2,2),c(2,2)).
1 <= {prec(c4(X_1,Y_1),c7(X_2,Y_2));prec(c7(X_2,Y_2),c4(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c4(X_1,Y_1),c(X_2,Y_2));prec(c(X_2,Y_2),c4(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c4(X_1,Y_1),c3(X_2,X_2));prec(c3(X_2,X_2),c4(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c4(X_1,Y_1),d6(X_2,X_2));prec(d6(X_2,X_2),c4(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c4(X_1,Y_1),a5(X_2,Y_2));prec(a5(X_2,Y_2),c4(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c4(X_1,Y_1),a(X_2,Y_2));prec(a(X_2,Y_2),c4(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c4(X_1,Y_1),d(X_2,X_2));prec(d(X_2,X_2),c4(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c7(X_1,Y_1),c(X_2,Y_2));prec(c(X_2,Y_2),c7(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c7(X_1,Y_1),c3(X_2,X_2));prec(c3(X_2,X_2),c7(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c7(X_1,Y_1),d6(X_2,X_2));prec(d6(X_2,X_2),c7(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c7(X_1,Y_1),a5(X_2,Y_2));prec(a5(X_2,Y_2),c7(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c7(X_1,Y_1),a(X_2,Y_2));prec(a(X_2,Y_2),c7(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c7(X_1,Y_1),d(X_2,X_2));prec(d(X_2,X_2),c7(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c(X_1,Y_1),c3(X_2,X_2));prec(c3(X_2,X_2),c(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c(X_1,Y_1),d6(X_2,X_2));prec(d6(X_2,X_2),c(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c(X_1,Y_1),a5(X_2,Y_2));prec(a5(X_2,Y_2),c(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c(X_1,Y_1),a(X_2,Y_2));prec(a(X_2,Y_2),c(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(c(X_1,Y_1),d(X_2,X_2));prec(d(X_2,X_2),c(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(c3(X_1,X_1),d6(X_2,X_2));prec(d6(X_2,X_2),c3(X_1,X_1))} <= 1 :- dom(X_1),dom(X_1), dom(X_2),dom(X_2).
1 <= {prec(c3(X_1,X_1),a5(X_2,Y_2));prec(a5(X_2,Y_2),c3(X_1,X_1))} <= 1 :- dom(X_1),dom(X_1), dom(X_2),dom(Y_2).
1 <= {prec(c3(X_1,X_1),a(X_2,Y_2));prec(a(X_2,Y_2),c3(X_1,X_1))} <= 1 :- dom(X_1),dom(X_1), dom(X_2),dom(Y_2).
1 <= {prec(c3(X_1,X_1),d(X_2,X_2));prec(d(X_2,X_2),c3(X_1,X_1))} <= 1 :- dom(X_1),dom(X_1), dom(X_2),dom(X_2).
1 <= {prec(d6(X_1,X_1),a5(X_2,Y_2));prec(a5(X_2,Y_2),d6(X_1,X_1))} <= 1 :- dom(X_1),dom(X_1), dom(X_2),dom(Y_2).
1 <= {prec(d6(X_1,X_1),a(X_2,Y_2));prec(a(X_2,Y_2),d6(X_1,X_1))} <= 1 :- dom(X_1),dom(X_1), dom(X_2),dom(Y_2).
1 <= {prec(d6(X_1,X_1),d(X_2,X_2));prec(d(X_2,X_2),d6(X_1,X_1))} <= 1 :- dom(X_1),dom(X_1), dom(X_2),dom(X_2).
1 <= {prec(a5(X_1,Y_1),a(X_2,Y_2));prec(a(X_2,Y_2),a5(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2).
1 <= {prec(a5(X_1,Y_1),d(X_2,X_2));prec(d(X_2,X_2),a5(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
1 <= {prec(a(X_1,Y_1),d(X_2,X_2));prec(d(X_2,X_2),a(X_1,Y_1))} <= 1 :- dom(X_1),dom(Y_1), dom(X_2),dom(X_2).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c4(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c4(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c4(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c7(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c7(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c7(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c(X_1,Y_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(c3(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(c3(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),c3(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(d6(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d6(X_1,X_1),d(X_2,X_2)), prec(d(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d6(X_1,X_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a5(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a5(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),a5(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),d6(X_2,X_2)), prec(d6(X_2,X_2),d(X_3,X_3)), prec(d(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d(X_3,X_3)), prec(d(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(a(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),a(X_1,Y_1)).
:- dom(X_1),dom(Y_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(a(X_1,Y_1),d(X_2,X_2)), prec(d(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),a(X_1,Y_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c4(X_2,Y_2)), prec(c4(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c7(X_2,Y_2)), prec(c7(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c(X_2,Y_2)), prec(c(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),d6(X_3,X_3)), prec(d6(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),c3(X_2,X_2)), prec(c3(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(X_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),d6(X_2,X_2)), prec(d6(X_2,X_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a5(X_2,Y_2)), prec(a5(X_2,Y_2),a(X_3,Y_3)), prec(a(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c4(X_3,Y_3)), prec(c4(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c7(X_3,Y_3)), prec(c7(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c(X_3,Y_3)), prec(c(X_3,Y_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),c3(X_3,X_3)), prec(c3(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(X_3), prec(d(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),d6(X_3,X_3)), prec(d6(X_3,X_3),d(X_1,X_1)).
:- dom(X_1),dom(X_1), dom(X_2),dom(Y_2), dom(X_3),dom(Y_3), prec(d(X_1,X_1),a(X_2,Y_2)), prec(a(X_2,Y_2),a5(X_3,Y_3)), prec(a5(X_3,Y_3),d(X_1,X_1)).
:- not sat.
sat :- sat_r5,sat_r6,sat_r7.
:- r5_5_unfound(1,1), a5(1,1).
:- r4_4_unfound(1,2), c4(1,2).
:- r4_4_unfound(1,1), c4(1,1).
:- r3_3_unfound(2,2), c3(2,2).
:- r3_3_unfound(1,1), c3(1,1).
:- r5_5_unfound(2,2), a5(2,2).
:- r6_6_unfound(1,1), d6(1,1).
:- r7_7_unfound(2,1), c7(2,1).
:- r4_4_unfound(2,1), c4(2,1).
:- r5_5_unfound(2,1), a5(2,1).
:- r7_7_unfound(1,1), c7(1,1).
:- r7_7_unfound(2,2), c7(2,2).
:- r7_7_unfound(1,2), c7(1,2).
:- r6_6_unfound(2,2), d6(2,2).
:- r4_4_unfound(2,2), c4(2,2).
:- r5_5_unfound(1,2), a5(1,2).
:- c3(1,1), #sum{1,0 : r3_unfound(1,1)} >=1 .
:- c3(2,2), #sum{1,0 : r3_unfound(2,2)} >=1 .
:- c4(1,1), #sum{1,0 : r4_unfound(1,1)} >=1 .
:- c4(1,2), #sum{1,0 : r4_unfound(1,2)} >=1 .
:- c4(2,1), #sum{1,0 : r4_unfound(2,1)} >=1 .
:- c4(2,2), #sum{1,0 : r4_unfound(2,2)} >=1 .
:- a5(1,1), #sum{1,0 : r5_unfound(1,1)} >=1 .
:- a5(2,1), #sum{1,0 : r5_unfound(2,1)} >=1 .
:- a5(1,2), #sum{1,0 : r5_unfound(1,2)} >=1 .
:- a5(2,2), #sum{1,0 : r5_unfound(2,2)} >=1 .
:- d6(1,1), #sum{1,0 : r6_unfound(1,1)} >=1 .
:- d6(2,2), #sum{1,0 : r6_unfound(2,2)} >=1 .
:- c7(1,1), #sum{1,0 : r7_unfound(1,1)} >=1 .
:- c7(1,2), #sum{1,0 : r7_unfound(1,2)} >=1 .
:- c7(2,1), #sum{1,0 : r7_unfound(2,1)} >=1 .
:- c7(2,2), #sum{1,0 : r7_unfound(2,2)} >=1 .
dom(1).
dom(2).
#show e/1.
#show c/2.
#show d/2.
#show a/2.
