p(X,Z) :- b(X,Y), c(Y,Z).

% I %
{ p(D,D2) : dom(D), dom(D2) }.

% MOD %
r1_x(1), r1_x(2), r1_x(3).
r1_y(1), r1_y(2), r1_y(3).
r1_z(1), r1_z(2), r1_z(3).

sat_r1 :- r1_x(1), r1_y(1), r1_z(1), not b(1,1).
sat_r1 :- r1_x(1), r1_y(1), r1_z(1), not c(1,1).
sat_r1 :- r1_x(1), r1_y(1), r1_z(1), p(1,1).

sat_r1 :- r1_x(1), r1_y(1), r1_z(2), not b(1,1).
sat_r1 :- r1_x(1), r1_y(1), r1_z(2), not c(1,2).
sat_r1 :- r1_x(1), r1_y(1), r1_z(2), p(1,2).

sat_r1 :- r1_x(1), r1_y(2), r1_z(1), not b(1,2).
sat_r1 :- r1_x(1), r1_y(2), r1_z(1), not c(2,1).
sat_r1 :- r1_x(1), r1_y(2), r1_z(1), p(1,1).

sat_r1 :- r1_x(1), r1_y(2), r1_z(2), not b(1,2).
sat_r1 :- r1_x(1), r1_y(2), r1_z(2), not c(2,2).
sat_r1 :- r1_x(1), r1_y(2), r1_z(2), p(1,2).

sat_r1 :- r1_x(2), r1_y(1), r1_z(1), not b(2,1).
sat_r1 :- r1_x(2), r1_y(1), r1_z(1), not c(1,1).
sat_r1 :- r1_x(2), r1_y(1), r1_z(1), p(2,1).

sat_r1 :- r1_x(2), r1_y(1), r1_z(2), not b(2,1).
sat_r1 :- r1_x(2), r1_y(1), r1_z(2), not c(1,2).
sat_r1 :- r1_x(2), r1_y(1), r1_z(2), p(2,2).

sat_r1 :- r1_x(2), r1_y(2), r1_z(1), not b(2,2).
sat_r1 :- r1_x(2), r1_y(2), r1_z(1), not c(2,1).
sat_r1 :- r1_x(2), r1_y(2), r1_z(1), p(2,1).

sat_r1 :- r1_x(2), r1_y(2), r1_z(2), not b(2,2).
sat_r1 :- r1_x(2), r1_y(2), r1_z(2), not c(2,2).
sat_r1 :- r1_x(2), r1_y(2), r1_z(2), p(2,2).

sat :- sat_r1.
:- not sat.

r1_x(1) :- sat.
r1_x(2) :- sat.

r1_y(1) :- sat.
r1_y(2) :- sat.

r1_z(1) :- sat.
r1_z(2) :- sat.

% FOUND %
1{y(D) : dom(D)}1 :- p(X,Z).

fp(X,Z) :- p(X,Z).

:- not fp(X,Z), p(X,Z).

% init %
dom(1).
dom(2).


