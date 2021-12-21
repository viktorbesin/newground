%xdom(1..400).
r(X) :- X=#min{ Y: edge(Y,_); Y: edge(_,Y) }.
:- not r(X), X=#max{ Y: edge(Y,_); Y: edge(_,Y) }.
{ f(X,Y) } :- edge(X,Y). %xdom(X),xdom(Y).
r(A) :- r(B), f(B,A), x(A). %f(B,A), f(C,A), f(B,C).
#program rules.
x(A) :- f(B,A), f(C,A), f(B,C), B != A, C != A, B != C.