import math


WEIGHTS = {
    "skill": 0.30,
    "distance": 0.20,
    "availability": 0.20,
    "rating": 0.15,
    "reliability": 0.10,
    "fair_opportunity": 0.05
}


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate approximate distance between two coordinates
    using the Haversine formula.
    """

    radius = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return radius * c


def normalize_rating(rating):
    """
    Convert 0-5 rating into 0-100 score.
    """

    return min(
        max((rating / 5) * 100, 0),
        100
    )


def normalize_reliability(reliability):
    """
    Reliability is already stored as a percentage.
    """

    return min(
        max(reliability, 0),
        100
    )


def calculate_distance_score(distance_km):
    """
    Convert distance into a 0-100 score.

    Closer workers receive a higher score.
    """

    if distance_km <= 1:
        return 100

    if distance_km >= 20:
        return 0

    score = 100 - (
        (distance_km - 1) / 19
    ) * 100

    return max(0, score)


def calculate_skill_score(worker, required_problem=None):
    """
    Estimate skill compatibility.

    For the MVP, skills are matched using keywords.
    """

    skills = worker.get("skills", "").lower()

    if not required_problem:
        return 80

    problem_words = (
        required_problem.lower()
        .replace("/", " ")
        .split()
    )

    matches = 0

    for word in problem_words:

        if len(word) > 2 and word in skills:
            matches += 1

    if matches >= 2:
        return 100

    if matches == 1:
        return 80

    return 60

def calculate_complex_skill_score(
    worker,
    required_components
):

    skills = worker.get(
        "skills",
        ""
    ).lower()

    if not required_components:
        return 80

    matches = 0

    for component in required_components:

        component_words = (
            component.lower()
            .split()
        )

        for word in component_words:

            if len(word) > 2 and word in skills:

                matches += 1
                break

    score = (
        matches / len(required_components)
    ) * 100

    return score
def calculate_availability_score(worker):
    availability = worker.get("availability", False)

    if availability is True:
        return 100

    return 0


def calculate_fair_opportunity_score(worker):
    """
    Give a small preference to workers who have completed
    fewer jobs, helping distribute opportunities more fairly.

    This is a prototype fairness mechanism.
    """

    completed_jobs = worker.get(
        "completed_jobs",
        0
    )

    if completed_jobs <= 20:
        return 100

    if completed_jobs >= 200:
        return 40

    score = 100 - (
        (completed_jobs - 20) / 180
    ) * 60

    return max(40, score)


def calculate_match_score(
    worker,
    customer_lat,
    customer_lon,
    required_problem=None,
    required_components=None
):
    worker_lat = worker.get(
        "latitude",
        customer_lat
    )

    worker_lon = worker.get(
        "longitude",
        customer_lon
    )

    distance_km = calculate_distance(
        customer_lat,
        customer_lon,
        worker_lat,
        worker_lon
    )

    if required_components:
        skill_score = calculate_complex_skill_score(
            worker,
            required_components
        )
    else:
        skill_score = calculate_skill_score(
            worker,
            required_problem
        )

    distance_score = calculate_distance_score(
        distance_km
    )

    availability_score = calculate_availability_score(
        worker
    )

    rating_score = normalize_rating(
        worker.get("rating", 0)
    )

    reliability_score = normalize_reliability(
        worker.get("reliability_score", 0)
    )

    fair_opportunity_score = calculate_fair_opportunity_score(
        worker
    )

    final_score = (
        skill_score * WEIGHTS["skill"]
        + distance_score * WEIGHTS["distance"]
        + availability_score * WEIGHTS["availability"]
        + rating_score * WEIGHTS["rating"]
        + reliability_score * WEIGHTS["reliability"]
        + fair_opportunity_score * WEIGHTS["fair_opportunity"]
    )

    return {
        "worker_id": worker.get("id"),
        "worker_name": worker.get("name"),
        "distance_km": round(distance_km, 2),
        "skill_score": round(skill_score, 2),
        "distance_score": round(distance_score, 2),
        "availability_score": round(availability_score, 2),
        "rating_score": round(rating_score, 2),
        "reliability_score": round(reliability_score, 2),
        "fair_opportunity_score": round(
            fair_opportunity_score,
            2
        ),
        "final_score": round(
            final_score,
            2
        )
    }
def rank_workers(
    workers,
    customer_lat,
    customer_lon,
    required_problem=None,
    required_components=None
):

    ranked_workers = []

    for worker in workers:

        availability = worker.get(
        "availability",
        False
    )

        if availability is not True:
            continue

        result = calculate_match_score(
           worker,
           customer_lat,
            customer_lon,
            required_problem,
            required_components
    )

        ranked_workers.append(result)

    ranked_workers.sort(
        key=lambda worker: worker["final_score"],
        reverse=True
    )

    return ranked_workers
def select_team(
    workers,
    team_size,
    customer_lat,
    customer_lon,
    required_problem=None,
    required_components=None
):

    ranked_workers = rank_workers(
    workers,
    customer_lat,
    customer_lon,
    required_problem,
    required_components
)

    selected_team = ranked_workers[:team_size]

    return {
        "team_size_requested": team_size,
        "team_size_selected": len(selected_team),
        "team_complete": len(selected_team) == team_size,
        "team_members": selected_team
    }
def generate_team_recommendation(
    team_matching
):

    requested = team_matching.get(
        "team_size_requested",
        0
    )

    selected = team_matching.get(
        "team_size_selected",
        0
    )

    complete = team_matching.get(
        "team_complete",
        False
    )

    shortage = max(
        requested - selected,
        0
    )

    if complete:

        return {
            "status": "Team Available",
            "shortage": 0,
            "recommendation": (
                "Required team is available."
            )
        }

    return {
        "status": "Team Incomplete",
        "shortage": shortage,
        "recommendation": (
            f"{shortage} additional worker(s) "
            "are required. "
            "Cooperative should activate or "
            "onboard additional workers."
        )
    }