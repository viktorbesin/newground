:- 2 <= #count{W : match(M1,W), match(M2,W), match(M3,W), M1 != M2, M1 != M3, M2 != M3}.
:- 2 <= #count{M : match(M,W1), match(M,W2), match(M,W3), W1 != W2, W1 != W3, W2 != W3}.

