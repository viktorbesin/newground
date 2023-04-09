
c(1) :- 2 <= #min{A,B,C,D: f(A,B), f(B,C), f(C,D), A != B, A != C, A != D, B != C, B != D, C != D}.
:- c(1).

