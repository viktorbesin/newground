

e(1).
c(1) :- b(1), prec(b(1), c(1)).
b(1) :- a(1), prec(a(1), b(1)).

1 <= {prec(b(1),c(1)); prec(c(1),b(1))} <= 1.
1 <= {prec(b(1),a(1)); prec(a(1),b(1))} <= 1.


