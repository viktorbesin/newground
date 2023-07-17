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
p(1,3).
p(2,8).
p(3,5).
p(4,7).
p(5,4).
p(6,1).
p(7,2).
p(8,9).
p(9,6).
patternlength(9).
kval(1).
kval(2).
kval(3).
kval(4).
kval(5).
kval(6).
kval(7).
kval(8).
kval(9).

% ENCODING ADDITIONAL PART
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
