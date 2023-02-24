edge(1,1).
edge(1,2).
edge(1,3).
edge(2,1).
edge(2,2).
edge(3,1).
edge(3,2).
edge(3,4).
edge(4,3).
edge(4,4).

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

