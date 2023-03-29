
active(P,E) :- p(P,E), not maintanace(P,E).
maintanace(P,E) :- p(P,E), not active(P,E).



