#show e/1.
#show c/1.
#show a/1.
#show b/1.

% (18):
e(1).
c(X) :- b(X).
b(X) :- a(X).

% New (25/26):
r1_unfound(1) :- not prec(c(1),b(1)).
r2_unfound(1) :- not prec(b(1),a(1)).
:- r1_unfound(1), c(1).
:- r2_unfound(1), b(1).

% Newground...
r3_X(1).
r3_X(1) :- sat.
sat_r3 :- r3_X(1),a'(1).
sat_r3 :- r3_X(1),not c(1).
domain_rule_3_variable_X(1).
{a'(X) : domain_rule_3_variable_X(X)} .
a(X) :- a'(X).
r3_unfound(1) :- not c(1).
r3_unfound(1) :- not prec(c(1),a(1)).

r4_X(1).
r4_X(1) :- sat.
sat_r4 :- r4_X(1),b'(1).
sat_r4 :- r4_X(1),not e(1).
domain_rule_4_variable_X(1).
{b'(X) : domain_rule_4_variable_X(X)} .
b(X) :- b'(X).
r4_unfound(1) :- not e(1).

% (20):
% macht keinen Unterschied ob disjunctive oder so (habs ausprobiert):
1 <= {prec(c(1),b(1));prec(b(1),c(1))} <= 1.
1 <= {prec(c(1),a(1));prec(a(1),c(1))} <= 1. 
1 <= {prec(b(1),a(1));prec(a(1),b(1))} <= 1.

% (21):
:- prec(c(1),b(1)), prec(b(1),a(1)), prec(a(1),c(1)).
:- prec(c(1),a(1)), prec(a(1),b(1)), prec(b(1),c(1)).
:- prec(b(1),c(1)), prec(c(1),a(1)), prec(a(1),b(1)).
:- prec(b(1),a(1)), prec(a(1),c(1)), prec(c(1),b(1)).
:- prec(a(1),c(1)), prec(c(1),b(1)), prec(b(1),a(1)).
:- prec(a(1),b(1)), prec(b(1),c(1)), prec(c(1),a(1)).

% REST:
:- not sat.
sat :- sat_r3,sat_r4.
:- a'(1), #sum{1,0 : r3_unfound(1)} >=1 .
:- b'(1), #sum{1,0 : r4_unfound(1)} >=1 .
dom(1).

