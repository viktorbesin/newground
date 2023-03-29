
violation(X,Y) :- edge(X,Y), g(X), g(Y).
violation(X,Y) :- edge(X,Y), b(X), b(Y).
violation(X,Y) :- edge(X,Y), r(X), r(Y).


violation_2(X,Y, 1) :- violation(X,Y).
violation_2(X,Y,Z2) :- violation_2(X,Y,Z), edge(A,Z2).

violation_3(X,Y, 1) :- violation(X,Y).
violation_3(X,Y,Z3) :- violation_3(X,Y,Z), edge(Z3,A).

violation_4(X,Y, 1) :- violation(X,Y).
violation_4(X,Y,Z4) :- violation_4(X,Y,Z), edge(A,Z4).

%my_test(1,1) :- #count{X,Y : violation(X,Y)} < 100.
%my_test(X+1,Y) :- my_test(X,Y), X < 10.
%my_test(X,Y + 1) :- my_test(X,Y), Y < 10.

%q(1) :- 5 <= #count{X1,Y1 : violation(X1,Y1,1)}.

:- 2 <= #count{X2,Y3,Z4 : violation_3(X3,Y3,Z3), violation_2(X2,Y2,Z2), violation_4(X4,Y4,Z4)}.

