import pytest
from app.dialect_engine import DialectEngine
from app.orchestrator import ConversationalOrchestrator
from app.matching_engine import CollectiveBatchSolver, calculate_gia_subsidy_split, haversine_distance_km
from app.main import sanitize_pdf_text
from app.database import init_db, SessionLocal, TrainingCenter


# ---------------------------------------------------------------------------
# Database & Core Engine Tests
# ---------------------------------------------------------------------------
def test_database_seeding():
    init_db()
    session = SessionLocal()
    centers_count = session.query(TrainingCenter).count()
    session.close()
    assert centers_count >= 3, f"Expected >= 3 centers, got {centers_count}"


# ---------------------------------------------------------------------------
# Dialect & Multi-Script Intent Tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("affirmative_input", [
    "haan", "ha", "haa", "haanji", "yes", "YEP", "sure", 
    "हाँ", "हाँजी", "हऊ", "हो", "sahi hai", "theek hai", "पक्का करें"
])
def test_affirmative_intent_variations(affirmative_input):
    assert DialectEngine.is_affirmative(affirmative_input) is True


@pytest.mark.parametrize("negative_input", [
    "nahi", "nahin", "no", "nope", "नहीं", "ना", "बाद में", "cancel"
])
def test_negative_intent_variations(negative_input):
    assert DialectEngine.is_negative(negative_input) is True


@pytest.mark.parametrize("query,expected_trade", [
    ("मुझे दुकान खोलनी है किराना स्टोर", "retail_business"),
    ("I run a small shop in village", "retail_business"),
    ("सोलर पैनल और सोलर लाइट का काम", "solar_installer"),
    ("solar fitting seekhna hai", "solar_installer"),
    ("कपड़े की सिलाई और कटिंग", "tailoring"),
    ("tailor master", "tailoring"),
    ("घर की वायरिंग और बिजली ठीक करना", "electrician"),
    ("kheti kisan vermicompost", "agriculture")
])
def test_trade_extraction_accuracy(query, expected_trade):
    assert DialectEngine.extract_trade(query) == expected_trade


# ---------------------------------------------------------------------------
# Conversational Orchestrator Journey Tests
# ---------------------------------------------------------------------------
def test_full_successful_dialogue_journey():
    session = {
        "session_id": "test-session-001",
        "current_step": "GREETING",
        "dialect": "hindi",
        "enrollment_confirmed": False
    }

    # Step 1: Greeting -> Consent
    _, session, finished, options, _ = ConversationalOrchestrator.advance_dialogue(
        session, "हाँ, शुरू करें", "hindi"
    )
    assert session["current_step"] == "ASK_NAME"
    assert session["voice_consent_granted"] is True
    assert finished is False

    # Step 2: Name Intake
    _, session, finished, options, _ = ConversationalOrchestrator.advance_dialogue(
        session, "Aadi Jain", "hindi"
    )
    assert session["current_step"] == "ASK_LOCATION"
    assert session["full_name"] == "Aadi Jain"

    # Step 3: Location Intake
    _, session, finished, options, _ = ConversationalOrchestrator.advance_dialogue(
        session, "Bhopal", "hindi"
    )
    assert session["current_step"] == "ASK_EDUCATION"
    assert session["village"] == "Bhopal"
    assert len(options) > 0

    # Step 4: Education Intake
    _, session, finished, options, _ = ConversationalOrchestrator.advance_dialogue(
        session, "12वीं पास", "hindi"
    )
    assert session["current_step"] == "ASK_WORK"

    # Step 5: Work / Aspiration Intake (Business)
    _, session, finished, options, _ = ConversationalOrchestrator.advance_dialogue(
        session, "दुकान व खुदरा व्यवसाय (Business)", "hindi"
    )
    assert session["current_step"] == "ORAL_TEST"
    assert session["aspired_trade"] == "retail_business"

    # Step 6: Oral RPL Diagnostic Test
    _, session, finished, options, courses = ConversationalOrchestrator.advance_dialogue(
        session, "बिक्री बहीखाता व स्टॉक रजिस्टर", "hindi"
    )
    assert session["current_step"] == "SELECT_COURSE"
    assert session["oral_rpl_score"] >= 0.90
    assert len(courses) > 0
    assert courses[0]["id"] == "RET/Q0101"

    # Step 7: Course Selection
    _, session, finished, options, _ = ConversationalOrchestrator.advance_dialogue(
        session, "Micro-Enterprise Retailer & Store Manager", "hindi"
    )
    assert session["current_step"] == "CONFIRM_ENROLLMENT"
    assert session["selected_course"]["id"] == "RET/Q0101"

    # Step 8: Confirmation
    _, session, finished, options, _ = ConversationalOrchestrator.advance_dialogue(
        session, "हाँ, नामांकन पक्का करें", "hindi"
    )
    assert session["current_step"] == "COMPLETED"
    assert session["enrollment_confirmed"] is True
    assert finished is True


# ---------------------------------------------------------------------------
# Matching & Solver Tests
# ---------------------------------------------------------------------------
def test_haversine_distance_accuracy():
    bhopal_lat, bhopal_lon = 23.2599, 77.4126
    mandideep_lat, mandideep_lon = 23.0722, 77.5186
    dist = haversine_distance_km(bhopal_lat, bhopal_lon, mandideep_lat, mandideep_lon)
    assert 18.0 <= dist <= 25.0


def test_gia_subsidy_split_math():
    result = calculate_gia_subsidy_split(unit_cost=100000)
    assert result["unit_cost"] == 100000
    assert result["grant_subsidy"] == 50000
    assert result["bank_loan"] == 40000
    assert result["beneficiary_equity"] == 10000


def test_milp_batch_solver_thresholds():
    solver = CollectiveBatchSolver(target_capacity=20, min_viable_threshold=12)

    # Test insufficient candidate pool (< 12)
    small_pool = [
        {"id": i, "aspired_trade": "solar_installer", "latitude": 23.2599, "longitude": 77.4126, "mobility_radius_km": 5.0}
        for i in range(5)
    ]
    centers = [{
        "id": 1,
        "center_name": "Gram Panchayat Bhawan",
        "center_type": "PANCHAYAT_BHAWAN",
        "block": "Phanda",
        "village": "Ratanpur",
        "latitude": 23.2599,
        "longitude": 77.4126
    }]

    batches = solver.solve_cohort_allocations(small_pool, centers, "solar_installer")
    assert len(batches) == 0

    # Test viable candidate pool (15 candidates)
    viable_pool = [
        {"id": i, "aspired_trade": "solar_installer", "latitude": 23.2599 + (i * 0.0001), "longitude": 77.4126, "mobility_radius_km": 5.0}
        for i in range(15)
    ]
    batches = solver.solve_cohort_allocations(viable_pool, centers, "solar_installer")
    assert len(batches) == 1
    assert batches[0]["enrolled_count"] == 15
    assert batches[0]["village"] == "Ratanpur"


# ---------------------------------------------------------------------------
# Document Sanitization Tests
# ---------------------------------------------------------------------------
def test_latin_safe_sanitization():
    indic_name = "आवेदक रमेश"
    sanitized = sanitize_pdf_text(indic_name)
    sanitized.encode('ascii')
    assert len(sanitized) > 0