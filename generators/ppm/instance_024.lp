t(1,10).
t(2,5).
t(3,2).
t(4,15).
t(5,12).
t(6,3).
t(7,7).
t(8,1).
t(9,14).
t(10,23).
t(11,24).
t(12,11).
t(13,22).
t(14,13).
t(15,6).
t(16,20).
t(17,4).
t(18,9).
t(19,8).
t(20,19).
t(21,21).
t(22,17).
t(23,18).
t(24,16).
p(1,5).
p(2,6).
p(3,8).
p(4,3).
p(5,2).
p(6,4).
p(7,7).
p(8,1).
patternlength(8).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
