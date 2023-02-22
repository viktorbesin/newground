% start is reachable
r(X) :- X=#min{ Y: edge(Y,_); Y: edge(_,Y) }.
% destination has to be reachable
:- not r(X), X=#max{ Y: edge(Y,_); Y: edge(_,Y) }.

% guess used edges / path
{ f(X,Y) } :- edge(X,Y).

% reachability
r(A) :- r(B), f(B,A).

#program rules.
% not more than 2 outgoing rules
:- f(B,A), f(B,C), A != C.
