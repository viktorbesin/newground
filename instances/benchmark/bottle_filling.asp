row(B,Y) :- bottle(B,X,Y).

{ fill(B,Y) } :- row(B,Y).

filled(X,Y) :- bottle(B,X,Y), fill(B,Y).
:- xvalue(Y,V), not #count{ X : filled(X,Y) } = V.
:- yvalue(X,V), not #count{ Y : filled(X,Y) } = V.

#program insts.
_dom_Y(Y) :- ysucc(Y,_).
_dom_Y(Y) :- ysucc(_,Y).
_dom_X(X) :- _dom_Y(X).

#program rules.
:- ysucc(Y,X), fill(B,Y), row(B,X), not fill(B,X).
