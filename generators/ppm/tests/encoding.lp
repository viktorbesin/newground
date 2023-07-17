% Check whether the subsequence is a matching
%:- solution(K1,ET1), solution(K2,ET2), p(K1,EP1), p(K2,EP2), ET1 < ET2, EP1 >= EP2.
:- 2 < #count{ET1 : solution(K1,ET1), solution(K2,ET2), p(K1,EP1), p(K2,EP2), ET1 < ET2, EP1 >= EP2}.
