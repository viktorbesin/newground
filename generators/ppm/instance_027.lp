t(1,5).
t(2,13).
t(3,25).
t(4,2).
t(5,23).
t(6,3).
t(7,14).
t(8,6).
t(9,1).
t(10,11).
t(11,10).
t(12,27).
t(13,20).
t(14,24).
t(15,26).
t(16,15).
t(17,7).
t(18,12).
t(19,22).
t(20,4).
t(21,9).
t(22,8).
t(23,19).
t(24,21).
t(25,17).
t(26,18).
t(27,16).
p(1,9).
p(2,6).
p(3,8).
p(4,7).
p(5,4).
p(6,2).
p(7,1).
p(8,5).
p(9,3).
patternlength(9).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
