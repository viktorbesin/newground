:- 2 <= #count{W : match(M1,W), match(M,W), M != M1}.
:- 2 <= #count{M : match(M,W), match(M,W1), W != W1}.

