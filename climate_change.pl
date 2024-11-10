justified_belief(greenhouse_effect_traps_heat) :-
    




% Facts (Premises)
greenhouse_effect_traps_heat.
human_activities_release_gases.
global_temperatures_increasing.
scientific_consensus_on_climate_change.
correlation_with_industrial_activity.

% Rules (Relationships between beliefs)
supports(human_activities_contribute_to_climate_change, greenhouse_effect_traps_heat).
supports(human_activities_contribute_to_climate_change, human_activities_release_gases).
supports(human_activities_contribute_to_climate_change, global_temperatures_increasing).
supports(human_activities_contribute_to_climate_change, scientific_consensus_on_climate_change).
supports(human_activities_contribute_to_climate_change, correlation_with_industrial_activity).

% Justified Belief (Conclusion)
justified_belief(human_activities_contribute_to_climate_change) :-
    greenhouse_effect_traps_heat,
    human_activities_release_gases,
    global_temperatures_increasing,
    scientific_consensus_on_climate_change,
    correlation_with_industrial_activity,
    supports(human_activities_contribute_to_climate_change, greenhouse_effect_traps_heat),
    supports(human_activities_contribute_to_climate_change, human_activities_release_gases),
    supports(human_activities_contribute_to_climate_change, global_temperatures_increasing),
    supports(human_activities_contribute_to_climate_change, scientific_consensus_on_climate_change),
    supports(human_activities_contribute_to_climate_change, correlation_with_industrial_activity).

% Query: Is the belief justified?
% ?- justified_belief(human_activities_contribute_to_climate_change).
