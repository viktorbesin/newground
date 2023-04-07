:- 2 <= #count{W : match(M1,W), match(M,W), match(M2,W), M != M1, M != M2, M1 != M2}.
:- 2 <= #count{M : match(M,W), match(M,W1), match(M,W2), W != W1, W != W2, W1 != W2}.

