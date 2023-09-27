c(1).
c(X) :- a(X).
a(X) :- b(X); not c(X).
a(X) :- c(X).
b(1).
c(1).
a(X) :- b(X), not c(X).
r3_X(1).
r3_X(1) :- sat.
sat_r3 :- r3_X(1),a(1).
sat_r3 :- r3_X(1),not b(1).
sat_r3 :- r3_X(1),c(1).
domain_rule_3_variable_X(1).
{a3(X) : domain_rule_3_variable_X(X)} .
a(X) :- a3(X).
r3_unfound(1) :- not b(1).
r3_unfound(1) :- c(1).
r4_X(1).
r4_X(1) :- sat.
sat_r4 :- r4_X(1),a(1).
sat_r4 :- r4_X(1),not c(1).
domain_rule_4_variable_X(1).
{a4(X) : domain_rule_4_variable_X(X)} .
a(X) :- a4(X).
r4_unfound(1) :- not c(1).
r4_unfound(1) :- not prec(c(1),a4(1)).
r4_4_unfound(1) :- not prec(a4(1),a(1)).
r5_X(1).
r5_X(1) :- sat.
sat_r5 :- r5_X(1),c(1).
sat_r5 :- r5_X(1),not a(1).
domain_rule_5_variable_X(1).
{c5(X) : domain_rule_5_variable_X(X)} .
c(X) :- c5(X).
r5_unfound(1) :- not a(1).
r5_unfound(1) :- not prec(a(1),c5(1)).
r5_5_unfound(1) :- not prec(c5(1),c(1)).
1 <= {prec(a(X_1),c(X_2));prec(c(X_2),a(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(a(X_1),c5(X_2));prec(c5(X_2),a(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(a(X_1),a(X_2));prec(a(X_2),a(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(a(X_1),a4(X_2));prec(a4(X_2),a(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(c(X_1),c5(X_2));prec(c5(X_2),c(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(c(X_1),c(X_2));prec(c(X_2),c(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(c(X_1),a(X_2));prec(a(X_2),c(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(c(X_1),a4(X_2));prec(a4(X_2),c(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(c5(X_1),c(X_2));prec(c(X_2),c5(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(c5(X_1),a(X_2));prec(a(X_2),c5(X_1))} <= 1 :- dom(X_1), dom(X_2).
1 <= {prec(c5(X_1),a4(X_2));prec(a4(X_2),c5(X_1))} <= 1 :- dom(X_1), dom(X_2).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),c(X_2)), prec(c(X_2),c5(X_3)), prec(c5(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),c(X_2)), prec(c(X_2),c(X_3)), prec(c(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),c(X_2)), prec(c(X_2),a(X_3)), prec(a(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),c(X_2)), prec(c(X_2),a4(X_3)), prec(a4(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),c5(X_2)), prec(c5(X_2),c(X_3)), prec(c(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),c5(X_2)), prec(c5(X_2),a(X_3)), prec(a(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),c5(X_2)), prec(c5(X_2),a4(X_3)), prec(a4(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),a(X_2)), prec(a(X_2),c(X_3)), prec(c(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),a(X_2)), prec(a(X_2),c5(X_3)), prec(c5(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),a(X_2)), prec(a(X_2),a4(X_3)), prec(a4(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),a4(X_2)), prec(a4(X_2),c(X_3)), prec(c(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),a4(X_2)), prec(a4(X_2),c5(X_3)), prec(c5(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a(X_1),a4(X_2)), prec(a4(X_2),a(X_3)), prec(a(X_3),a(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),a(X_2)), prec(a(X_2),c5(X_3)), prec(c5(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),a(X_2)), prec(a(X_2),c(X_3)), prec(c(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),a(X_2)), prec(a(X_2),a(X_3)), prec(a(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),a(X_2)), prec(a(X_2),a4(X_3)), prec(a4(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),c5(X_2)), prec(c5(X_2),a(X_3)), prec(a(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),c5(X_2)), prec(c5(X_2),c(X_3)), prec(c(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),c5(X_2)), prec(c5(X_2),a4(X_3)), prec(a4(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),c(X_2)), prec(c(X_2),a(X_3)), prec(a(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),c(X_2)), prec(c(X_2),c5(X_3)), prec(c5(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),c(X_2)), prec(c(X_2),a4(X_3)), prec(a4(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),a4(X_2)), prec(a4(X_2),a(X_3)), prec(a(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),a4(X_2)), prec(a4(X_2),c5(X_3)), prec(c5(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c(X_1),a4(X_2)), prec(a4(X_2),c(X_3)), prec(c(X_3),c(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),a(X_2)), prec(a(X_2),c(X_3)), prec(c(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),a(X_2)), prec(a(X_2),a(X_3)), prec(a(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),a(X_2)), prec(a(X_2),a4(X_3)), prec(a4(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),c(X_2)), prec(c(X_2),a(X_3)), prec(a(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),c(X_2)), prec(c(X_2),c(X_3)), prec(c(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),c(X_2)), prec(c(X_2),a4(X_3)), prec(a4(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),a4(X_2)), prec(a4(X_2),a(X_3)), prec(a(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(c5(X_1),a4(X_2)), prec(a4(X_2),c(X_3)), prec(c(X_3),c5(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),a(X_2)), prec(a(X_2),c(X_3)), prec(c(X_3),a4(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),a(X_2)), prec(a(X_2),c5(X_3)), prec(c5(X_3),a4(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),a(X_2)), prec(a(X_2),a(X_3)), prec(a(X_3),a4(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),c(X_2)), prec(c(X_2),a(X_3)), prec(a(X_3),a4(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),c(X_2)), prec(c(X_2),c5(X_3)), prec(c5(X_3),a4(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),c(X_2)), prec(c(X_2),c(X_3)), prec(c(X_3),a4(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),c5(X_2)), prec(c5(X_2),a(X_3)), prec(a(X_3),a4(X_1)).
:- dom(X_1), dom(X_2), dom(X_3), prec(a4(X_1),c5(X_2)), prec(c5(X_2),c(X_3)), prec(c(X_3),a4(X_1)).
:- not sat.
sat :- sat_r3,sat_r4,sat_r5.
:- r5_5_unfound(1), c5(1).
:- r4_4_unfound(1), a4(1).
:- a3(1), #sum{1,0 : r3_unfound(1)} >=1 .
:- a4(1), #sum{1,0 : r4_unfound(1)} >=1 .
:- c5(1), #sum{1,0 : r5_unfound(1)} >=1 .
dom(1).
#show b/1.
#show c/1.
#show a/1.
