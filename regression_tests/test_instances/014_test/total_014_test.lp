#program facts.
p(1).

#program rules.
p(Y) :- p(X), p(Y), Y = X + 1, Y < 5.
