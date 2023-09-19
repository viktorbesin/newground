
a(1,1).
a(2,2).
a(1,2).
a(2,1).

b(1,1).
b(2,2).
b(1,2).
b(2,1).


#program rules.

z(X,Y) :- a(X,Y), not b(X,Y).

y(X,Y) :- z(X,Y).
x(X,Y) :- y(X,Y).
z(X,Y) :- x(X,Y).



