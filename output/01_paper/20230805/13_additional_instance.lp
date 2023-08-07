{f(X,Y)} :- edge(X,Y).

f(Y,X) :- f(X,Y).

rch(X) :- X = #min{A: f(A,_); B: f(_,B)}.
rch(Y) :- rch(X), f(X,Y).
rch(X) :- rch(Y), f(X,Y).

% Hard constraint
%number_vertices(N) :- N = #count{X : vertex(X)}.
%min_reached_vertices(M) :- number_vertices(N), M = N * 0.8.

:- #count{X: rch(X)} < M, min_reached_vertices(M).

% Graph must be connected
:- f(X,Y), not rch(X).


% No two distributor nodes must be adjacent
%:- distributor(A), distributor(B), f(A,B), A != B.
% No two distributor nodes must have a distance between them of 2
%:- distributor(A), distributor(B), f(A,X), f(X,B), A != X, X != B.

% Replace method
%c(X) :- X = #count{A: distributor(A)}.

% Rewriting
%c(1) :- 5 <= #count{A: f(A,B), f(A,C), f(A,D), ..., A != B, A != C, A != D, B != C, B != D, C != D}.
%c(X) :- X = #count{A: distributor(A)}.


%:~ f(X,Y). [1@1,X,Y]
%:~ d(X). [100*X@1,X]

% Or something like that? -> To add other aggregates like min/max -> ''Schachtelung''
%:- #max{X: c(X)} < 5.


