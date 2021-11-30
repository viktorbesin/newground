xdom(1..100).
{ q(X,Y) } :- xdom(X),xdom(Y).
{ z(X,Y) } :- xdom(X),xdom(Y).
{ x(X,Y) } :- xdom(X),xdom(Y).
{ t(X,Y) } :- xdom(X),xdom(Y).
{ w(X,Y) } :- xdom(X),xdom(Y).
%#program rules.
y(A) :- z(A,B), q(A,C), w(B,C), not t(A,C).
