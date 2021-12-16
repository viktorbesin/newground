%xdom(1..400).
{ f(X,Y) } :- e(X,Y). %xdom(X),xdom(Y).
r(A) :- r(B), x(A,B). %f(B,A), f(C,A), f(B,C).
#program rules.
x(A,B) :- f(B,A), f(C,A), f(B,C), B != A, C != A, B != C.
