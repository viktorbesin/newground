t(1,28).
t(2,20).
t(3,5).
t(4,25).
t(5,22).
t(6,2).
t(7,3).
t(8,14).
t(9,11).
t(10,6).
t(11,1).
t(12,13).
t(13,10).
t(14,24).
t(15,26).
t(16,27).
t(17,15).
t(18,7).
t(19,12).
t(20,23).
t(21,4).
t(22,9).
t(23,8).
t(24,19).
t(25,21).
t(26,17).
t(27,18).
t(28,16).
p(1,2).
p(2,5).
p(3,8).
p(4,7).
p(5,6).
p(6,9).
p(7,4).
p(8,3).
p(9,1).
patternlength(9).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
