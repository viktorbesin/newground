t(1,29).
t(2,26).
t(3,5).
t(4,22).
t(5,23).
t(6,2).
t(7,3).
t(8,14).
t(9,11).
t(10,6).
t(11,1).
t(12,13).
t(13,10).
t(14,20).
t(15,28).
t(16,25).
t(17,27).
t(18,15).
t(19,7).
t(20,12).
t(21,24).
t(22,4).
t(23,9).
t(24,8).
t(25,19).
t(26,21).
t(27,17).
t(28,18).
t(29,16).
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
