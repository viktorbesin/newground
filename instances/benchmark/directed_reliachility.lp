xdom(1..400).
{ f(X,Y) } :- xdom(X),xdom(Y).
r(A) :- r(B), r(C), e(A). %f(B,A), f(C,A), f(B,C).
#program rules.
e(A) :- f(B,A), f(C,A), f(B,C), B != A, C != A, B != C.
