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


