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


