seed(30770).
num_vertices(10).
edge_probability(20).
repetition(1).
vertex(1).
vertex(2).
vertex(3).
vertex(4).
vertex(5).
vertex(6).
vertex(7).
vertex(8).
vertex(9).
vertex(10).
edge(1,2).
edge(1,8).
edge(2,9).
edge(3,1).
edge(3,7).
edge(5,2).
edge(5,3).
edge(5,9).
edge(5,10).
edge(6,2).
edge(6,3).
edge(6,4).
edge(7,1).
edge(8,5).
edge(9,2).
edge(10,6).
{ f(X,Y) } :- edge(X,Y).
rch(X) :- X = #min { A: f(A,_); B: f(_,B) }.
rch(Y) :- rch(X),f(X,Y).
rch(X) :- rch(Y),f(X,Y).
#false :- M > #count { X: rch(X) },min_reached_vertices(M).
#false :- f(X,Y),not rch(X).


