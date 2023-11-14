manAssignsScore(1,1,1).
manAssignsScore(1,1,2).
manAssignsScore(1,1,3).
manAssignsScore(1,1,4).
manAssignsScore(1,1,5).
manAssignsScore(1,1,6).
manAssignsScore(1,1,7).
manAssignsScore(1,1,8).
manAssignsScore(1,1,9).
womanAssignsScore(1,1,1).
womanAssignsScore(1,1,2).
womanAssignsScore(1,1,3).
womanAssignsScore(1,1,4).
womanAssignsScore(1,1,5).
womanAssignsScore(1,1,6).
womanAssignsScore(1,1,7).
womanAssignsScore(1,1,8).
womanAssignsScore(1,1,9).
match(M,W) :- manAssignsScore(M,_,_),womanAssignsScore(W,_,_),not nonMatch(M,W).
nonMatch(M,W) :- manAssignsScore(M,_,_),womanAssignsScore(W,_,_),not match(M,W).
jailed(M) :- match(M,_).
#false :- manAssignsScore(M,_,_),not jailed(M).
#false :- match(M,W1),manAssignsScore(M,W,Smw),W1 != W,manAssignsScore(M,W1,Smw1),Smw > Smw1,match(M1,W),womanAssignsScore(W,M,Swm),womanAssignsScore(W,M1,Swm1),Swm >= Swm1.

#program rules.
#false :- M2_0 != M3_0,M1_1 != M3_1,match(M2_0,W_0),M1_0 != M2_0,match(M3_0,W_0),M1_0 != M3_0,W_0!=W_1,M2_1 != M3_1,match(M3_1,W_1),M1_1 != M2_1,match(M1_1,W_1),match(M2_1,W_1),match(M1_0,W_0).
#false :- W1_0 != W2_0,W1_1 != W2_1,match(M_1,W1_1),W1_0 != W3_0,match(M_0,W2_0),M_0!=M_1,W2_0 != W3_0,match(M_0,W3_0),match(M_1,W2_1),W2_1 != W3_1,match(M_1,W3_1),match(M_0,W1_0),W1_1 != W3_1.
