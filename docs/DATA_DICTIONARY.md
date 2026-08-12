# Data Dictionary — FIFA World Cup 2026

## matches.csv
| Column | Type | Description |
|--------|------|-------------|
| match_id | int | Primary key |
| date | date | Match date |
| home_team_id | int | FK to teams |
| away_team_id | int | FK to teams |
| home_score | int | Goals scored by home team |
| away_score | int | Goals scored by away team |
| stage_id | int | FK to tournament_stages |
| venue_id | int | FK to venues |
| referee_id | int | FK to referees |

## teams.csv
| Column | Type | Description |
|--------|------|-------------|
| team_id | int | Primary key |
| team_name | str | Full team name |
| fifa_code | str | 3-letter FIFA code |
| group_letter | str | Group assignment (A-L) |
| confederation | str | Confederation name |
| fifa_ranking_pre_tournament | int | Pre-tournament ranking |

## match_team_stats.csv
| Column | Type | Description |
|--------|------|-------------|
| match_id | int | FK to matches |
| team_id | int | FK to teams |
| possession_pct | float | Possession percentage |
| total_shots | int | Total shots |
| shots_on_target | int | Shots on target |
| passes | int | Total passes |
| pass_accuracy_pct | float | Pass accuracy |
| fouls | int | Fouls committed |
| yellow_cards | int | Yellow cards |
| red_cards | int | Red cards |
| offsides | int | Offsides |
| corners | int | Corners |
| crosses | int | Crosses |
| saves | int | Goalkeeper saves |

## player_stats.csv
| Column | Type | Description |
|--------|------|-------------|
| player_id | int | Primary key |
| team_id | int | FK to teams |
| player_name | str | Player name |
| position | str | Playing position |
| minutes_played | int | Total minutes |
| goals | int | Goals scored |
| assists | int | Assists |
| shots | int | Total shots |
| shots_on_target | int | Shots on target |
| passes | int | Passes completed |
| pass_accuracy_pct | float | Pass accuracy |
| tackles | int | Tackles |
| interceptions | int | Interceptions |
| yellow_cards | int | Yellow cards |
| red_cards | int | Red cards |
| fouls | int | Fouls committed |
| (more columns exist) | | |

## venues.csv
| Column | Type | Description |
|--------|------|-------------|
| venue_id | int | Primary key |
| stadium_name | str | Stadium name |
| city | str | City |
| country | str | Country |
| capacity | int | Stadium capacity |
| elevation_m | float | Elevation in meters |
| opening_date | date | Opening date |

## referees.csv
| Column | Type | Description |
|--------|------|-------------|
| referee_id | int | Primary key |
| name | str | Referee name |
| country | str | Nationality |

## tournament_stages.csv
| Column | Type | Description |
|--------|------|-------------|
| stage_id | int | Primary key |
| stage_name | str | Stage name |
| is_knockout | bool | Is knockout stage |

## match_events.csv
| Column | Type | Description |
|--------|------|-------------|
| event_id | int | Primary key |
| match_id | int | FK to matches |
| team_id | int | FK to teams |
| player_id | int | FK to players |
| event_type | str | Event type (goal, card, etc.) |
| minute | int | Match minute |
| (additional columns) | | |

## squads_and_players.csv
| Column | Type | Description |
|--------|------|-------------|
| player_id | int | Primary key |
| team_id | int | FK to teams |
| player_name | str | Player name |
| position | str | Position |
| shirt_number | int | Jersey number |
| date_of_birth | date | DOB |
| height_cm | int | Height |

## matches_detailed.csv
| Column | Type | Description |
|--------|------|-------------|
| match_id | int | FK to matches |
| home_formation | str | Home formation |
| away_formation | str | Away formation |
| home_xg | float | Home xG |
| away_xg | float | Away xG |
| attendance | int | Attendance |

## match_prediction_features.csv
| Column | Type | Description |
|--------|------|-------------|
| match_id | int | FK to matches |
| (various features) | | Prediction features |

## match_lineups.csv
| Column | Type | Description |
|--------|------|-------------|
| match_id | int | FK to matches |
| team_id | int | FK to teams |
| player_id | int | FK to players |
| is_starter | bool | Starting XI |
| position | str | Position in match |