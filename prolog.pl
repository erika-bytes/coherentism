% Fact
%likes(mary, pizza).

% Rule
%likes(john, X) :- likes(mary, X).
%is_at(mary,park)

%know(fact,X):- fact(X)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
is_angry(ellie).
has_motive(Y):- is_angry(Y).
is_at(ellie,crimescene).

is_guilty(X) :- is_at(X,crimescene), has_motive(X).