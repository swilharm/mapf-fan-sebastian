abstraction.
#include <incmode>.

% Neeeded when running solve.lp on its own
%robotsMoving(N) :- N= #count{R:start(R,_)}.

at(R,V,0) :- chosen(R,V).
{chosen(R,S) : start(R,S)} = N :- robotsMoving(N).
{ assigned(R,S,G,V) : goal(G,V) } = 1 :- chosen(R,S).
:- goal(G,_), assigned(R1,_,G,_), assigned(R2,_,G,_), R1<R2.
:- start(R,_), assigned(R,_,G1,_), assigned(R,_,G2,_), G1<G2.

#program step(t).
{ move(R,V1,V2,t) : edge(V1,V2) } 1 :- chosen(R,_), at(R,V1,t-1).
move(R,V1,V2,t) :- at(R,V1,t-1), at(R,V2,t), V1!=V2.
#heuristic move(C,V1,V2,T).[1,false]

at(R,V2,t) :- move(R,V1,V2,t).
at(R,V1,t) :- at(R,V1,t-1), not move(R,V1,_,t).

conflict(R1,R2,t) :- at(R1,V,t), at(R2,V,t), R1<R2. 
% edge conflict
conflict(R1,R2,t) :- at(R1,V1,t-1), at(R1,V2,t), at(R2,V2,t-1), at(R2,V1,t), R1<R2.
% path crossing conflict
conflict(R1,R2,t) :- at(R1,V1,t-1), at(R2,V2,t-1), at(R1,V3,t), at(R2,V4,t),
	node(X,Y,V1), node(X+1,Y,V2), node(X+1,Y+1,V3), node(X,Y+1,V4).
conflict(R1,R2,t) :- at(R1,V1,t-1), at(R2,V2,t-1), at(R1,V3,t), at(R2,V4,t),
	node(X,Y,V1), node(X+1,Y,V2), node(X+1,Y-1,V3), node(X,Y-1,V4).
conflict(R1,R2,t) :- at(R1,V1,t-1), at(R2,V2,t-1), at(R1,V3,t), at(R2,V4,t),
	node(X,Y,V1), node(X,Y+1,V2), node(X+1,Y+1,V3), node(X+1,Y,V4).
conflict(R1,R2,t) :- at(R1,V1,t-1), at(R2,V2,t-1), at(R1,V3,t), at(R2,V4,t),
	node(X,Y,V1), node(X,Y+1,V2), node(X-1,Y+1,V3), node(X-1,Y,V4).
#minimize{1@100,R1,R2,T : conflict(R1,R2,T)}.
#program conflicts(t).
:- conflict(_,_,t).

#program check(t).
#external query(t).
:- goal(G,V), start(R,S), assigned(R,S,G,V), not at(R,V,t), query(t).

#show.
%#show at/3.
%#show move/4.
%#show conflict/3.
%#show assigned/4.

% Output for visualizer (requires instance file as well)
#show occurs(object(robot,R), action(move,(DX,DY)), T) : move(R,V1,V2,T), node(X1,Y1,V1), node(X2,Y2,V2), DX=X2-X1, DY=Y2-Y1.