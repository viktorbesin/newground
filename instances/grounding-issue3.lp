xdom(1..10).
{ q(X) } :- xdom(X).
{ z(X) } :- xdom(X).
{ x(X) } :- xdom(X).
%#program rules.
y(A) :- z(A), q(B), x(C).
