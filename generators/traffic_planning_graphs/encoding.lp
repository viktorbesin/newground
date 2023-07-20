distributor(A) :- f(A,B), f(A,C), f(A,D), f(A,E), f(A,F), f(A,G), f(A,H), f(A,I), A != B, A != C, A != D, A != E, A != F, A != G, A != H, A != I, B != C, B != D, B != E, B != F, B != G, B != H, B != I, C != D, C != E, C != F, C != G, C != H, C != I, D != E, D != F, D != G, D != H, D != I, E != F, E != G, E != H, E != I, F != G, F != H, F != I, G != H, G != I, H != I. % f(B,C), f(C,D), f(D,F), f(F,I), f(I,H), f(H,G), f(E,G), f(B,E).


%distributor_node_count(X) :- X = #count{A : f(A,B), f(A,C), f(A,D), f(A,E), f(A,F), f(A,G), f(A,H), f(A,I), A != B, A != C, A != D, A != E, A != F, A != G, A != H, A != I, B != C, B != D, B != E, B != F, B != G, B != H, B != I, C != D, C != E, C != F, C != G, C != H, C != I, D != E, D != F, D != G, D != H, D != I, E != F, E != G, E != H, E != I, F != G, F != H, F != I, G != H, G != I, H != I. % f(B,C), f(C,D), f(D,F), f(F,I), f(I,H), f(H,G), f(E,G), f(B,E)}.

