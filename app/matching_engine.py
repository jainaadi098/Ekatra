# app/matching_engine.py
import json
import math
from typing import List, Dict, Any
from app.database import get_db

EDU_HIERARCHY = {
    "No Formal Education": 0,
    "5th Pass": 1,
    "8th Pass": 2,
    "10th Pass": 3,
    "12th Pass": 4,
    "ITI/Diploma": 5,
    "Graduate": 6
}

COURSE_MIN_EDU = {
    "None": 0,
    "5th Class": 1,
    "8th Class": 2,
    "10th Class": 3,
    "10th Class or ITI": 3,
    "12th Class": 4
}

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def match_nsqf_pathways(slots: Dict[str, Any], user_lat: float = 23.2599, user_lon: float = 77.4126) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.qp_code, c.qp_name, c.sector, c.nsqf_level, c.entry_req, c.training_hours, c.is_enterprise, c.description, c.features_json,
           t.name as center_name, t.partner_type, t.lat as center_lat, t.lon as center_lon
    FROM nsqf_courses c
    JOIN training_centers t ON c.qp_code = t.qp_code
    """)
    rows = cursor.fetchall()
    conn.close()

    beneficiary_edu = slots.get("formal_education") or "No Formal Education"
    user_edu_rank = EDU_HIERARCHY.get(beneficiary_edu, 0)
    trade_query = (slots.get("traditional_trade") or "").lower()
    is_self_employed_pref = slots.get("employment_type") == "SELF_EMPLOYED"
    mobility_km = float(slots.get("mobility_radius_km") or 25)

    ranked_results = []

    for row in rows:
        min_required_rank = COURSE_MIN_EDU.get(row["entry_req"], 0)
        features = json.loads(row["features_json"])
        
        has_prior_trade_experience = any(term in trade_query or trade_query in term for term in features)
        is_rpl_route = False

        if user_edu_rank < min_required_rank:
            if has_prior_trade_experience:
                is_rpl_route = True
            else:
                continue

        score = 0.35

        if has_prior_trade_experience:
            score += 0.40

        if is_self_employed_pref and row["is_enterprise"] == 1:
            score += 0.20
        elif not is_self_employed_pref and row["is_enterprise"] == 0:
            score += 0.15

        dist = calculate_haversine_distance(user_lat, user_lon, row["center_lat"], row["center_lon"])
        if dist > mobility_km:
            score -= 0.25
        else:
            score += 0.05

        score = max(0.15, min(0.99, score))

        # Financial Linkage Engine: PM-AJAY GIA Component (50% Grant Capped at ₹50,000)
        if is_self_employed_pref:
            estimated_project_cost = 100000
            gia_capital_subsidy = min(50000, int(estimated_project_cost * 0.50))
            margin_money = int(estimated_project_cost * 0.10)
            bank_loan = estimated_project_cost - gia_capital_subsidy - margin_money

            gia_subsidy = {
                "scheme": "PM-AJAY GIA Capital Subsidy (Self-Employment)",
                "grant_amount": f"₹{gia_capital_subsidy:,} (50% Project Cost)",
                "financial_structure": f"Grant: ₹{gia_capital_subsidy:,} | Bank Loan (MUDRA/NSFDC): ₹{bank_loan:,} | Beneficiary Margin: ₹{margin_money:,}",
                "type": "Direct Capital Toolkit / Machinery Grant",
                "nodal_agency": "State Scheduled Castes Development Corporation (SCDC)"
            }
        else:
            gia_subsidy = {
                "scheme": "PM-AJAY Wage Skilling & Placement Linkage",
                "grant_amount": "100% Free Training + Post-Placement Allowance",
                "financial_structure": "Centrally Sponsored under Common Cost Norms",
                "type": "Assured Industry Apprenticeship / Placement",
                "nodal_agency": "National Skill Development Corporation (NSDC)"
            }

        effective_duration = "40-80 Hours (Accelerated RPL Track)" if is_rpl_route else f"{row['training_hours']} Hours"

        ranked_results.append({
            "qp_code": row["qp_code"],
            "qp_name": row["qp_name"],
            "sector": row["sector"],
            "nsqf_level": row["nsqf_level"],
            "entry_req": row["entry_req"],
            "is_rpl_bridge": is_rpl_route,
            "training_hours": effective_duration,
            "center_name": row["center_name"],
            "center_type": row["partner_type"],
            "distance_km": dist,
            "match_confidence": int(score * 100),
            "gia_benefit": gia_subsidy,
            "description": row["description"]
        })

    ranked_results.sort(key=lambda x: (x["match_confidence"], -x["distance_km"]), reverse=True)
    return ranked_results[:3]