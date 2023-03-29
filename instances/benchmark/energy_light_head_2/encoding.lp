:- 0 <= #min{E1: active(P1,E1), active(P2, E2), active(P3, E3), active(P4, E4), P1 != P2, P1 != P3, P1 != P4, P2 != P3, P2 != P4, P3 != P4, E1 + E2 >= 1000, E1 + E3 >= 1000, E1 + E4 >= 1000,  E2 + E3 >= 1000, E2 + E3 >= 1000, E3 + E4 >= 1000} <= 100.

%:- 0 <= #min{E1: active(P1,E1), active(P2, E2), active(P3, E3), loc(P1, X1), loc(P2,X2), loc(P3, X3), X1 - X3 <= 100, X1 - X2 <= 100, X2 - X3 <= 100, P1 != P2, P1 != P3, P2 != P3, E1 != E2, E1 != E3, E2 != E3} <= 100.
%:- 0 <= #min{E1 : active(P1,E1), active(P2, E2), active(P3,E3), active(P4,E4), active(P5,E5), active(P6,E6), P1 != P2, P1 != P3, P1 != P4, P1 != P5, P1 != P6, P2 != P3, P2 != P4, P2 != P5, P2 != P6, P3 != P4, P3 != P5, P3 != P6, P4 != P5, P4 != P6, E1 - E2 <= 100} <= 100.



