:- 10 <= #count{W : match(M1,W), match(M2,W), match(M3,W), M1 != M2, M1 != M3, M2 != M3}.
:- 10 <= #count{M : match(M,W1), match(M,W2), match(M,W3), W1 != W2, W1 != W3, W2 != W3}.
:- 2 <= #count{W : match(M1,W), match(M2,W), match(M3,W), match(M4,W), match(M5,W), M1 != M2, M1 != M3, M1 != M4, M1 != M5, M2 != M3, M2 != M4, M2 != M5, M3 != M4, M3 != M5, M4 != M5}.
:- 2 <= #count{M : match(M,W1), match(M,W2), match(M,W3), match(M,W4), match(M,W5), W1 != W2, W1 != W3, W1 != W4, W1 != W5, W2 != W3, W2 != W4, W2 != W5, W3 != W4, W3 != W5, W4 != W5}.
