%xdom(1..400).
{ f(X,Y) } :- e(X,Y). %xdom(X),xdom(Y).
r(A) :- r(B), f(B,A). %f(B,A), f(C,A), f(B,C).
#program rules.
%not more than 3 outgoing rules
:- f(B,A), f(B,C), f(B,D), A != C, C != D, A != D.
