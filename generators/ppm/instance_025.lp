t(1,5).
t(2,10).
t(3,7).
t(4,2).
t(5,25).
t(6,3).
t(7,15).
t(8,6).
t(9,1).
t(10,14).
t(11,22).
t(12,23).
t(13,11).
t(14,24).
t(15,13).
t(16,12).
t(17,20).
t(18,4).
t(19,9).
t(20,8).
t(21,19).
t(22,21).
t(23,17).
t(24,18).
t(25,16).
p(1,5).
p(2,7).
p(3,6).
p(4,4).
p(5,2).
p(6,1).
p(7,8).
p(8,3).
patternlength(8).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
