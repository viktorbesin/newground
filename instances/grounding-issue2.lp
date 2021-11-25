xdom(1..1000).
{ q(X) } :- xdom(X).
{ z(X) } :- xdom(X).
{ x(X) } :- xdom(X).
y(A) :- z(A), q(B), x(C).
