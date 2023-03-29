

%:- 2 <= #count{X,Y : violation(X,Y), violation_2(A,B), violation_3(C,D), not X = A, not Y = B, not C = A, not D = B}.
:- 2 <= #count{X,Y : violation(X,Y), violation_2(A,B), violation_3(C,D), X != A, Y != B, C != A, D != B}.
