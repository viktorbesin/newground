#program facts.
body(1,1).
body(1,2).
body(2,2).
body(3,3).

#program rules.
% Equivalent to: success_1 :- 2 <= #count{X,Y:body(X,Y)}.
success_1_b :- 2 <= #count{X,Y:body(X,Y)}.
success_1 :- body(X1, Y1), body(X2, Y2), 0 != (X1 ^ X2) ? (Y1 ^ Y2).
% Equivalent to: success_2 :- 3 <= #count{X,Y:body(X,Y)}.
success_2_b :- 3 <= #count{X,Y:body(X,Y)}.
success_2 :- body(X1, Y1), body(X2, Y2), body(X3, Y3), 0 != (X1 ^ X2) ? (Y1 ^ Y2), 0 != (X1 ^ X3) ? (Y1 ^ Y3), 0 != (X2 ^ X3) ? (Y2 ^ Y3).
 
% Count
partial_sum(O,1) :- first(O,X1).
partial_sum(O2,S2) :- next(O1,O2,X2), partial_sum(O1,S1), S2 = S1 + 1.
sum(S) :- last(O,X2), partial_sum(O,S).

% Sum
%partial_sum(O,X1) :- first(O,X1).
%partial_sum(O2,S2) :- next(O1,O2,X2), partial_sum(O1,S1), S2 = S1 + X2.
%sum(S) :- last(O,X2), partial_sum(O,S).

first(body(X1,Y1), X1) :- body(X1,Y1), #false : body(X2,Y2), body(X2, Y2) < body(X1, Y1).
next(body(X1,Y1), body(X2,Y2), X2) :- body(X1,Y1), body(X2, Y2), body(X1,Y1) < body(X2,Y2), #false : body(X3,Y3), body(X1, Y1) < body(X3, Y3), body(X3,Y3) < body(X2, Y2).
last(body(X2,Y2), X2) :- body(X2,Y2), #false : body(X1,Y1), body(X2,Y2) < body(X1,Y1).

