t(1,12).
t(2,1).
t(3,7).
t(4,6).
t(5,8).
t(6,14).
t(7,3).
t(8,13).
t(9,2).
t(10,5).
t(11,4).
t(12,10).
t(13,11).
t(14,15).
t(15,9).
t(16,16).
p(1,4).
p(2,5).
p(3,2).
p(4,1).
p(5,3).
patternlength(5).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
