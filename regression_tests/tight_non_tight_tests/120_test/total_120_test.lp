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
vertex(11).
vertex(12).
vertex(13).
vertex(14).
vertex(15).
vertex(16).
vertex(17).
vertex(18).
vertex(19).
edge(1,10).
edge(1,14).
edge(1,18).
edge(2,3).
edge(2,6).
edge(2,8).
edge(2,11).
edge(2,14).
edge(2,16).
edge(3,4).
edge(3,6).
edge(3,11).
edge(3,13).
edge(3,14).
edge(3,16).
edge(4,10).
edge(4,11).
edge(4,13).
edge(5,12).
edge(5,13).
edge(5,15).
edge(6,1).
edge(6,2).
edge(6,15).
edge(6,18).
edge(7,6).
edge(7,7).
edge(7,8).
edge(7,9).
edge(7,11).
edge(7,13).
edge(7,17).
edge(7,18).
edge(8,6).
edge(8,10).
edge(8,14).
edge(8,17).
edge(9,1).
edge(9,7).
edge(9,10).
edge(9,18).
edge(10,5).
edge(10,12).
edge(10,13).
edge(11,1).
edge(11,2).
edge(11,6).
edge(11,17).
edge(12,9).
edge(12,10).
edge(13,3).
edge(13,4).
edge(13,6).
edge(14,6).
edge(14,7).
edge(14,10).
edge(14,11).
edge(15,16).
edge(16,6).
edge(16,14).
edge(16,15).
edge(16,17).
edge(16,19).
edge(17,2).
edge(17,18).
edge(18,4).
edge(18,14).
edge(18,16).
edge(19,1).
edge(19,4).
edge(19,5).
edge(19,8).
edge(19,14).
keep(X) :- vertex(X),not delete(X).
delete(X) :- vertex(X),not keep(X).
#false :- delete(X),vertex(Y),not keep(Y),X != Y.
kept_edge(V1,V2) :- keep(V1),keep(V2),edge(V1,V2).
reachable(X,Y) :- kept_edge(X,Y).
blue(N) :- keep(N),not red(N),not green(N).
red(N) :- keep(N),not blue(N),not green(N).
green(N) :- keep(N),not red(N),not blue(N).
#false :- kept_edge(N1,N2),blue(N1),blue(N2).
#false :- kept_edge(N1,N2),red(N1),red(N2).
#false :- kept_edge(N1,N2),green(N1),green(N2).
reachable(X,Z) :- delete(D),edge(X,D),reachable(X,Y),reachable(Y,Z).

#program rules.
#false :- edge(V1_0,D_0),reachable(V1_1,V2_1),delete(D_0),delete(D_1),edge(D_1,V2_1),D_0!=D_1,edge(V1_1,D_1),reachable(V1_0,V2_0),edge(D_0,V2_0).
