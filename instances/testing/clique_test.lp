{ f(X,Y) } :-X=1..4, Y=1..4, X < Y. 
#program rules.
r(A):- f(A,B), f(A,C), f(B,C), A < B, B < C.
#show f/2.
