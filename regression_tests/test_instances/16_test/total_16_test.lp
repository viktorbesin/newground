edge(1,1).
edge(1,2).
edge(1,3).
edge(1,6).
edge(1,8).
edge(1,9).
edge(2,1).
edge(2,2).
edge(2,5).
edge(2,7).
edge(3,1).
edge(3,2).
edge(3,4).
edge(3,5).
edge(3,8).
edge(4,3).
edge(4,4).
edge(4,6).
edge(5,7).
edge(5,8).
edge(6,1).
edge(6,3).
edge(6,4).
edge(6,5).
edge(6,8).
edge(6,9).
edge(7,1).
edge(7,2).
edge(7,6).
edge(7,8).
edge(8,1).
edge(8,3).
edge(8,4).
edge(8,5).
edge(8,6).
edge(8,8).
edge(8,9).
edge(9,1).
edge(9,7).


% guess coloring
{ g(X,Y); b(X,Y); r(X,Y) } :- edge(X,Y). 

% only one color
:- g(X,Y), b(X,Y).
:- g(X,Y), r(X,Y). 
:- r(X,Y), b(X,Y).

#program rules.
% not coloring 2 outgoing edges the same 
:- g(X,Y), g(X,Z), Y < Z.
:- b(X,Y), b(X,Z), Y < Z.
:- r(X,Y), r(X,Z), Y < Z.

% not coloring 2 ingoing edges the same 
:- g(Y,X), g(Z,X), Y < Z.
:- r(Y,X), r(Z,X), Y < Z.
:- b(Y,X), b(Z,X), Y < Z.

