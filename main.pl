% objects
# person(x).
location().
# time().
# motive().

# % Relationships
# friend_of()
# enemy_of()
was_at(Person,Location,Time)

% Rules
# cannot_be_at_two_locations_time(X, Y, Z, Q, W) :- 
#   was_at(X, Y, Z),
#   was_at(X, W, Q),
#   Y \= W.
#   Z \= Q.

cannot_be_at_two_locations_time(was_at(X,Y,Z),was_at(X,W,Q)) :- 
  was_at(X, Y, Z),
  was_at(X, W, Q),
  Y \= W.
  Z \= Q.


location(park)
location(house)
person(ellie)
time(nine)
time(eight)

# was_at(ellie,park,nine)
# was_at(ellie,house,nine)

# % single_location(X,Y) :- was_at()

# % Query 1
# ?
# % Query 2
# ?
