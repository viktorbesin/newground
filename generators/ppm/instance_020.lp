t(1,3).
t(2,10).
t(3,15).
t(4,1).
t(5,7).
t(6,5).
t(7,13).
t(8,12).
t(9,20).
t(10,19).
t(11,11).
t(12,14).
t(13,6).
t(14,4).
t(15,2).
t(16,9).
t(17,8).
t(18,17).
t(19,18).
t(20,16).
p(1,5).
p(2,4).
p(3,1).
p(4,2).
p(5,6).
p(6,3).
patternlength(6).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
