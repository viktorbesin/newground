row(B,Y) :- bottle(B,X,Y).

{ fill(B,Y) } :- row(B,Y).

filled(X,Y) :- bottle(B,X,Y), fill(B,Y).
:- xvalue(Y,V), not #count{ X : filled(X,Y) } = V.
:- yvalue(X,V), not #count{ Y : filled(X,Y) } = V.

#program rules.
:- ysucc(Y1,Y2), fill(B,Y1), row(B,Y2), not fill(B,Y2).
