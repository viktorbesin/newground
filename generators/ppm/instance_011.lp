t(1,6).
t(2,5).
t(3,11).
t(4,2).
t(5,1).
t(6,3).
t(7,7).
t(8,4).
t(9,10).
t(10,9).
t(11,8).
p(1,1).
p(2,2).
p(3,3).
patternlength(3).

% ENCODING ADDITIONAL PART
kval(1).
kval(N+1) :- kval(N), N < L, patternlength(L). 
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
