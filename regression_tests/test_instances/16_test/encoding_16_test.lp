% not coloring 2 outgoing edges the same 
:- g(X,Y), g(X,Z), Y < Z.
:- b(X,Y), b(X,Z), Y < Z.
:- r(X,Y), r(X,Z), Y < Z.

% not coloring 2 ingoing edges the same 
:- g(Y,X), g(Z,X), Y < Z.
:- r(Y,X), r(Z,X), Y < Z.
:- b(Y,X), b(Z,X), Y < Z.

