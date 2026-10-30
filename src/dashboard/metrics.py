def calculate_unavailability_rate(
    zero_bike_observations: int,
    eligible_observations: int
) -> float:
    if eligible_observations <= 0:
        return 0.0
    return (
        zero_bike_observations / eligible_observations
    ) * 100