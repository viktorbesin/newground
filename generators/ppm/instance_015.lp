t(1,13).
t(2,1).
t(3,6).
t(4,12).
t(5,7).
t(6,3).
t(7,15).
t(8,2).
t(9,5).
t(10,4).
t(11,10).
t(12,11).
t(13,14).
t(14,9).
t(15,8).
p(1,3).
p(2,4).
p(3,2).
p(4,1).
p(5,5).
patternlength(5).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
