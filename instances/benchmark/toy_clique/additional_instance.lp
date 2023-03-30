
x(X,Y) :- edge(X,Y).
f(X,Y) :- x(X,Y), not x_1(X,Y).
x_1(X,Y) :- x(X,Y), not f(X,Y).

%{f(X,Y)} :- edge(X,Y).


