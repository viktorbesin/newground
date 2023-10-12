z(X,Y) :- a(X,Y), not b(X,Y).

y(X,Y) :- z(X,Y).
x(X,Y) :- y(X,Y).
z(X,Y) :- x(X,Y).



