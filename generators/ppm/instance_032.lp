t(1,11).
t(2,5).
t(3,23).
t(4,22).
t(5,24).
t(6,10).
t(7,2).
t(8,32).
t(9,13).
t(10,3).
t(11,28).
t(12,29).
t(13,16).
t(14,6).
t(15,14).
t(16,1).
t(17,20).
t(18,30).
t(19,15).
t(20,7).
t(21,12).
t(22,26).
t(23,4).
t(24,9).
t(25,25).
t(26,8).
t(27,19).
t(28,21).
t(29,27).
t(30,17).
t(31,18).
t(32,31).
p(1,4).
p(2,3).
p(3,8).
p(4,6).
p(5,1).
p(6,10).
p(7,5).
p(8,7).
p(9,9).
p(10,2).
patternlength(10).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
