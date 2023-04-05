
% not coloring 2 outboing edges the same (if happens twice, or more often)
:- 2 <= #count{X : g(X,Y), g(X,Z), Y < Z}.
:- 2 <= #count{X : b(X,Y), b(X,Z), Y < Z}.
:- 2 <= #count{X : r(X,Y), r(X,Z), Y < Z}.

% not coloring 2 outboing edges the same (if happens twice, or more often)
:- 2 <= #count{X : g(Y,X), g(Z,X), Y < Z}.
:- 2 <= #count{X : b(Y,X), b(Z,X), Y < Z}.
:- 2 <= #count{X : r(Y,X), r(Z,X), Y < Z}.

