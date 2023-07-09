t(1,7).
t(2,12).
t(3,14).
t(4,6).
t(5,3).
t(6,2).
t(7,1).
t(8,5).
t(9,4).
t(10,10).
t(11,11).
t(12,13).
t(13,9).
t(14,8).
p(1,4).
p(2,1).
p(3,3).
p(4,2).
patternlength(4).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
