
%q(1) :- 10 <= #count{X1,Y1 : violation(X1,Y1,1)}.

:- 2 <= #max{X,Y : violation(X,Y), violation_2(A,B), violation_3(C,D), not X = A, not Y = B, not C = A, not D = B}.

