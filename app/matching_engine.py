import math
from typing import List, Dict, Any
from ortools.linear_solver import pywraplp


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(dlambda / 2.0) ** 2)
    return 2.0 * r * math.asin(math.sqrt(a))


class CollectiveBatchSolver:
    def __init__(self, target_capacity: int = 20, min_viable_threshold: int = 12):
        self.target_capacity = target_capacity
        self.min_viable_threshold = min_viable_threshold

    def solve_cohort_allocations(
        self,
        candidates: List[Dict[str, Any]],
        centers: List[Dict[str, Any]],
        trade: str
    ) -> List[Dict[str, Any]]:
        pool = [c for c in candidates if c.get("aspired_trade") == trade]

        if len(pool) < self.min_viable_threshold:
            return []

        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return []

        num_c = len(pool)
        num_h = len(centers)

        x = {}
        for i in range(num_c):
            for j in range(num_h):
                x[i, j] = solver.BoolVar(f"x_{i}_{j}")

        y = {}
        for j in range(num_h):
            y[j] = solver.BoolVar(f"y_{j}")

        # Constraint 1: A candidate can be assigned to at most one training hub
        for i in range(num_c):
            solver.Add(solver.Sum(x[i, j] for j in range(num_h)) <= 1)

        # Constraint 2: Hub capacity boundaries
        for j in range(num_h):
            solver.Add(solver.Sum(x[i, j] for i in range(num_c)) >= self.min_viable_threshold * y[j])
            solver.Add(solver.Sum(x[i, j] for i in range(num_c)) <= self.target_capacity * y[j])

        # Constraint 3: Geofence and distance limits
        for i in range(num_c):
            c_lat, c_lon = pool[i]["latitude"], pool[i]["longitude"]
            max_d = pool[i].get("mobility_radius_km", 5.0)

            for j in range(num_h):
                h_lat, h_lon = centers[j]["latitude"], centers[j]["longitude"]
                dist = haversine_distance_km(c_lat, c_lon, h_lat, h_lon)
                if dist > max_d:
                    solver.Add(x[i, j] == 0)

        # Objective Function: Maximize aggregate assignment with proximity reward
        objective = solver.Objective()
        for i in range(num_c):
            c_lat, c_lon = pool[i]["latitude"], pool[i]["longitude"]
            for j in range(num_h):
                dist = haversine_distance_km(c_lat, c_lon, centers[j]["latitude"], centers[j]["longitude"])
                weight = 100.0 - dist
                objective.SetCoefficient(x[i, j], weight)

        objective.SetMaximization()
        solver.Solve()

        batches = []
        for j in range(num_h):
            if y[j].solution_value() > 0.5:
                assigned_candidates = [
                    pool[i]["id"] for i in range(num_c)
                    if x[i, j].solution_value() > 0.5
                ]
                batches.append({
                    "center_id": centers[j]["id"],
                    "center_name": centers[j]["center_name"],
                    "center_type": centers[j]["center_type"],
                    "village": centers[j].get("village", centers[j]["block"]),
                    "trade": trade,
                    "enrolled_count": len(assigned_candidates),
                    "target_capacity": self.target_capacity,
                    "candidate_ids": assigned_candidates,
                    "status": "LOCKED" if len(assigned_candidates) >= self.target_capacity else "FORMING"
                })

        return batches


def calculate_gia_subsidy_split(unit_cost: int = 100000) -> Dict[str, Any]:
    grant = min(int(unit_cost * 0.50), 50000)
    loan = int(unit_cost * 0.40)
    equity = int(unit_cost * 0.10)
    return {
        "unit_cost": unit_cost,
        "grant_subsidy": grant,
        "bank_loan": loan,
        "beneficiary_equity": equity,
        "grant_formatted": f"₹{grant:,}",
        "loan_formatted": f"₹{loan:,}",
        "equity_formatted": f"₹{equity:,}"
    }