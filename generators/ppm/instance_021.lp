t(1,3).
t(2,10).
t(3,2).
t(4,1).
t(5,7).
t(6,5).
t(7,14).
t(8,12).
t(9,19).
t(10,20).
t(11,11).
t(12,15).
t(13,13).
t(14,6).
t(15,21).
t(16,4).
t(17,9).
t(18,8).
t(19,17).
t(20,18).
t(21,16).
p(1,6).
p(2,4).
p(3,5).
p(4,1).
p(5,2).
p(6,7).
p(7,3).
patternlength(7).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
