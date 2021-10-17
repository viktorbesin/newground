p(X,Z) :- b(X,Y), c(Y, Z).

% init %
dom(1..2).

b(1,2).
c(2,1).

b(1,1).
c(1,2).
c(1,1).

#show p/2.
