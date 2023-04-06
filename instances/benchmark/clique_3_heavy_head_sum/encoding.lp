
c(1) :- 2 <= #sum{A,B,C: f(A,B), f(B,C), A != B, A != C, B != C}.
:- c(1).

