t(1,3).
t(2,9).
t(3,7).
t(4,1).
t(5,12).
t(6,15).
t(7,10).
t(8,17).
t(9,11).
t(10,6).
t(11,4).
t(12,2).
t(13,5).
t(14,14).
t(15,13).
t(16,8).
t(17,16).
p(1,2).
p(2,4).
p(3,1).
p(4,5).
p(5,3).
patternlength(5).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
