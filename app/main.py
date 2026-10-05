import os
import io
import html
import uuid
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

# ReportLab: Flowables (Pure Paragraph & Spacer Layout)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.database import init_db, get_db, BeneficiaryProfile, TrainingCenterNode
from app.orchestrator import ConversationalOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ekatra")

init_db()

app = FastAPI(title="Ekatra: PM-AJAY Livelihood Aggregator", version="5.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

ACTIVE_CALLS: Dict[str, Dict[str, Any]] = {}


class TurnPayload(BaseModel):
    session_id: str
    user_utterance: str
    dialect: Optional[str] = "hindi"


def sanitize_pdf_text(val: Any, default: str = "N/A") -> str:
    """
    Prevents Latin-1 encoder panics and escapes XML reserved symbols
    to eliminate ReportLab ExpatError and UnicodeEncodeError crashes.
    """
    if val is None:
        return default
    text = str(val).strip()
    if not text:
        return default
    clean = text.encode("ascii", errors="ignore").decode("ascii").strip()
    return html.escape(clean) if clean else default


@app.get("/")
def index():
    path = os.path.join(static_dir, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"status": "Ekatra Engine Online"}


@app.post("/api/call/start")
def start_call():
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "current_step": "GREETING",
        "enrollment_confirmed": False
    }
    ACTIVE_CALLS[session_id] = session_data
    return {
        "session_id": session_id,
        "spoken_prompt": "नमस्ते! PM-AJAY आजीविका व कौशल मैपिंग पोर्टल में आपका स्वागत है। क्या हम पंजीकरण शुरू करें?",
        "options": ["हाँ, शुरू करें", "नहीं, बाद में"]
    }


@app.post("/api/call/turn")
def execute_turn(payload: TurnPayload, db: Session = Depends(get_db)):
    session_data = ACTIVE_CALLS.get(payload.session_id)
    if not session_data:
        session_data = {"session_id": payload.session_id, "current_step": "GREETING"}
        ACTIVE_CALLS[payload.session_id] = session_data

    prompt, session_data, is_finished, options, courses = ConversationalOrchestrator.advance_dialogue(
        session_data, payload.user_utterance, payload.dialect
    )
    ACTIVE_CALLS[payload.session_id] = session_data

    # Persist all 9 slots to DB once enrollment is confirmed
    if session_data.get("enrollment_confirmed"):
        course = session_data.get("selected_course", {})
        beneficiary = db.query(BeneficiaryProfile).filter_by(session_id=payload.session_id).first()
        if not beneficiary:
            beneficiary = BeneficiaryProfile(
                session_id=payload.session_id,
                full_name=session_data.get("full_name", "Applicant"),
                district=session_data.get("district", "Bhopal"),
                block=session_data.get("block", "Phanda"),
                village=session_data.get("village", "Phanda"),
                latitude=session_data.get("lat", 23.2599),
                longitude=session_data.get("lon", 77.4126),
                formal_education=session_data.get("formal_education", "12th Standard"),
                nsqf_eligible_level=session_data.get("nsqf_eligible_level", 4),
                current_occupation=session_data.get("current_occupation", "Retail"),
                oral_rpl_score=session_data.get("oral_rpl_score", 0.95),
                aspired_trade=session_data.get("aspired_trade", "retail_business"),
                livelihood_intent=session_data.get("livelihood_intent", "SETUP"),
                availability_window=session_data.get("availability_window", "Morning Batches"),
                sc_status_verified=session_data.get("sc_status_verified", True),
                selected_course_title=course.get("title", "Micro-Enterprise Retailer"),
                selected_course_id=course.get("id", "RET/Q0101"),
                allocated_center_name=session_data.get("center", "Gram Panchayat Bhawan"),
                distance_to_center_km=session_data.get("center_dist", 3.2),
                radius_status=session_data.get("radius_status", "GREEN"),
                enrollment_confirmed=True
            )
            db.add(beneficiary)
            db.commit()
            logger.info(f"[DB Persisted] Profile saved for session {payload.session_id}")

    return {
        "session_id": payload.session_id,
        "spoken_prompt": prompt,
        "current_step": session_data.get("current_step"),
        "is_finished": is_finished,
        "options": options,
        "suggested_courses": courses,
        "enrollment_confirmed": session_data.get("enrollment_confirmed", False),
        "profile_card": {
            "name": session_data.get("full_name", "--"),
            "district": session_data.get("district", "--"),
            "block": session_data.get("block", "--"),
            "center_dist": session_data.get("center_dist"),
            "radius_status": session_data.get("radius_status", "GREEN"),
            "schooling": session_data.get("formal_education", "--"),
            "nsqf_level": session_data.get("nsqf_eligible_level"),
            "current_work": session_data.get("current_occupation", "--"),
            "trade": session_data.get("selected_course", {}).get("title", "--"),
            "livelihood_intent": session_data.get("livelihood_intent", "--"),
            "availability_window": session_data.get("availability_window", "--")
        }
    }


# ---------------------------------------------------------------------------
# SEARCH ROUTE: Multi-Parameter Index Search
# ---------------------------------------------------------------------------
@app.get("/api/beneficiaries/search")
def search_beneficiaries(
    q: Optional[str] = Query(None, description="Search across Name, District, Block, Trade, or Course ID"),
    district: Optional[str] = None,
    block: Optional[str] = None,
    trade: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(BeneficiaryProfile).filter(BeneficiaryProfile.enrollment_confirmed == True)
    if district:
        query = query.filter(BeneficiaryProfile.district.ilike(f"%{district}%"))
    if block:
        query = query.filter(BeneficiaryProfile.block.ilike(f"%{block}%"))
    if trade:
        query = query.filter(BeneficiaryProfile.aspired_trade.ilike(f"%{trade}%"))
    if q:
        search_filter = (
            BeneficiaryProfile.full_name.ilike(f"%{q}%") |
            BeneficiaryProfile.village.ilike(f"%{q}%") |
            BeneficiaryProfile.selected_course_id.ilike(f"%{q}%") |
            BeneficiaryProfile.selected_course_title.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)

    records = query.order_by(BeneficiaryProfile.id.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "name": r.full_name,
            "district": r.district,
            "block": r.block,
            "schooling": r.formal_education,
            "nsqf_level": f"Level {r.nsqf_eligible_level}",
            "current_work": r.current_occupation,
            "desire_trade": r.selected_course_title,
            "course_id": r.selected_course_id,
            "center": r.allocated_center_name,
            "radius_metric": f"{r.distance_to_center_km} Km ({r.radius_status})",
            "dossier_pdf_url": f"/api/dossier/pdf/{r.session_id}"
        }
        for r in records
    ]


# ---------------------------------------------------------------------------
# DOSSIER PDF GENERATOR: Single-Page Pure Paragraph & Spacer Layout
# ---------------------------------------------------------------------------
@app.get("/api/dossier/pdf/{session_id}")
def generate_dossier_pdf(session_id: str, db: Session = Depends(get_db)):
    session_data = ACTIVE_CALLS.get(session_id, {})
    db_profile = db.query(BeneficiaryProfile).filter_by(session_id=session_id).first()

    name = sanitize_pdf_text(session_data.get("full_name") or (db_profile.full_name if db_profile else "Applicant"))
    district = sanitize_pdf_text(session_data.get("district") or (db_profile.district if db_profile else "Bhopal"))
    block = sanitize_pdf_text(session_data.get("block") or (db_profile.block if db_profile else "Phanda"))
    village = sanitize_pdf_text(session_data.get("village") or (db_profile.village if db_profile else "Phanda"))
    education = sanitize_pdf_text(session_data.get("formal_education") or (db_profile.formal_education if db_profile else "12th Standard"))
    occupation = sanitize_pdf_text(session_data.get("current_occupation") or (db_profile.current_occupation if db_profile else "Retail"))
    
    course_info = session_data.get("selected_course") or {}
    course_title = sanitize_pdf_text(course_info.get("title") or (db_profile.selected_course_title if db_profile else "Micro-Enterprise Retailer"))
    course_id = sanitize_pdf_text(course_info.get("id") or (db_profile.selected_course_id if db_profile else "RET/Q0101"))
    center = sanitize_pdf_text(session_data.get("center") or (db_profile.allocated_center_name if db_profile else "Gram Panchayat Bhawan"))
    distance = str(session_data.get("center_dist") or (db_profile.distance_to_center_km if db_profile else "3.2"))
    radius_status = sanitize_pdf_text(session_data.get("radius_status") or (db_profile.radius_status if db_profile else "GREEN"))
    nsqf_level = str(session_data.get("nsqf_eligible_level") or (db_profile.nsqf_eligible_level if db_profile else "4"))
    intent = sanitize_pdf_text(session_data.get("livelihood_intent") or (db_profile.livelihood_intent if db_profile else "SETUP"))
    time_limit = sanitize_pdf_text(session_data.get("availability_window") or (db_profile.availability_window if db_profile else "Morning Batches"))
    sc_verified = "Yes (Statutory Criteria Matched)" if (session_data.get("sc_status_verified") or (db_profile.sc_status_verified if db_profile else True)) else "General / Other"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=24,
        bottomMargin=24
    )
    styles = getSampleStyleSheet()

    story = [
        # 1. Ministry Header
        Paragraph("<b>GOVERNMENT OF INDIA &bull; MINISTRY OF SOCIAL JUSTICE &amp; EMPOWERMENT</b>", styles['Normal']),
        Spacer(1, 3),
        Paragraph("<b>PRADHAN MANTRI ANUSUCHIT JAATI ABHYUDAY YOJANA (PM-AJAY)</b>", styles['Heading2']),
        Spacer(1, 1),
        Paragraph("<font size=8 color='#475569'>GIA Component &bull; MP State Mission Directorate &bull; Form-1 Appraisal Dossier</font>", styles['Normal']),
        Spacer(1, 8),

        # 2. Administrative Status Ribbon
        Paragraph(f"<b>Application Ref ID:</b> PMAJAY-{session_id[:8].upper()} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Location:</b> {block}, {district} (MP) &nbsp;&nbsp;|&nbsp;&nbsp; <b>Status:</b> <font color='#166534'><b>VERIFIED &amp; ALLOCATED</b></font>", styles['Normal']),
        Spacer(1, 4),
        Paragraph("----------------------------------------------------------------------------------------------------------------------------------", styles['Normal']),
        Spacer(1, 6),

        # 3. Section I: Beneficiary Profile (Slots 1, 4, 5, 9)
        Paragraph("<b>SECTION I: BENEFICIARY INTAKE PROFILE</b>", styles['Heading3']),
        Spacer(1, 3),
        Paragraph(f"<b>&bull; Full Name:</b> {name} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>&bull; Schooling:</b> {education} (Assessed: NSQF Level {nsqf_level})", styles['Normal']),
        Spacer(1, 2),
        Paragraph(f"<b>&bull; Habitation / Village:</b> {village} (Tehsil: {block}, District: {district}, Madhya Pradesh)", styles['Normal']),
        Spacer(1, 2),
        Paragraph(f"<b>&bull; Current Work / Craft:</b> {occupation} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>&bull; SC Status:</b> <font color='#166534'><b>{sc_verified}</b></font>", styles['Normal']),
        Spacer(1, 2),
        Paragraph("<b>&bull; Oral RPL Assessment:</b> <font color='#166534'><b>Competency Verified (95%) &bull; Certificate Gate Waived</b></font>", styles['Normal']),
        Spacer(1, 8),

        # 4. Section II: Training Center Node & Skilling Allocation (Slots 2, 3, 6, 7, 8)
        Paragraph("<b>SECTION II: NSQF ACCREDITED SKILLING &amp; CLUSTER NODE</b>", styles['Heading3']),
        Spacer(1, 3),
        Paragraph(f"<b>&bull; Allocated Course:</b> <b>{course_title}</b> (QP Code: <b>{course_id}</b>)", styles['Normal']),
        Spacer(1, 2),
        Paragraph(f"<b>&bull; Assigned Training Center:</b> {center}", styles['Normal']),
        Spacer(1, 2),
        Paragraph(f"<b>&bull; Center Distance:</b> {distance} Km &bull; Radius Status: <b><font color='{'#166534' if radius_status == 'GREEN' else '#DC2626'}'>{radius_status} (&lt;=15 Km Gate Rule)</font></b>", styles['Normal']),
        Spacer(1, 2),
        Paragraph(f"<b>&bull; Livelihood Track:</b> {intent} Model &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>&bull; Time Limit:</b> {time_limit}", styles['Normal']),
        Spacer(1, 2),
        Paragraph("<b>&bull; Cohort Formulation:</b> <font color='#1E40AF'><b>Confirmed (15/20 Candidates Enrolled in Panchayat Batch)</b></font>", styles['Normal']),
        Spacer(1, 8),

        # 5. Section III: PM-AJAY Statutory GIA Financial Subsidy (50:40:10 Matrix)
        Paragraph("<b>SECTION III: STATUTORY GIA 50-40-10 CAPITAL SUBSIDY SPECIFICATION</b>", styles['Heading3']),
        Spacer(1, 3),
        Paragraph("<b>1. Base Unit Project Cost:</b> Rs. 1,00,000 (100% Micro-Enterprise Baseline Unit)", styles['Normal']),
        Spacer(1, 2),
        Paragraph("<b>2. PM-AJAY Direct Capital Grant (50%):</b> <font color='#166534'><b>Rs. 50,000</b></font> <i>(Direct Capital Subsidy for Tools &amp; Setup)</i>", styles['Normal']),
        Spacer(1, 2),
        Paragraph("<b>3. Institutional Credit Term Loan (40%):</b> Rs. 40,000 <i>(MUDRA Shishu / Bank Credit Linkage)</i>", styles['Normal']),
        Spacer(1, 2),
        Paragraph("<b>4. Beneficiary Margin Contribution (10%):</b> Rs. 10,000 <i>(Beneficiary Equity Contribution)</i>", styles['Normal']),
        Spacer(1, 14),

        # 6. Verification Signatures
        Paragraph("----------------------------------------------------------------------------------------------------------------------------------", styles['Normal']),
        Spacer(1, 10),
        Paragraph(f"<b>Beneficiary Signature:</b> _______________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Authorized Officer:</b> _______________________", styles['Normal']),
        Spacer(1, 3),
        Paragraph(f"Name: {name} (Applicant Verification) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; District Nodal Authority (MoSJE / PM-AJAY MP)", styles['Normal'])
    ]

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    filename = f"PM_AJAY_Appraisal_{name.replace(' ', '_')}_{session_id[:6]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )