# app/database.py
import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "pmajay_prototype.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Beneficiary Master Store
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS beneficiaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        phone TEXT DEFAULT '9876543210',
        block_name TEXT DEFAULT 'Phanda (Bhopal)',
        preferred_language TEXT DEFAULT 'hi',
        formal_education TEXT,
        traditional_trade TEXT,
        current_work TEXT,
        employment_type TEXT,
        mobility_radius_km INTEGER DEFAULT 15,
        location_lat REAL DEFAULT 23.2599,
        location_lon REAL DEFAULT 77.4126,
        raw_aspiration TEXT,
        is_complete INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # NSQF Qualification Packs Master
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nsqf_courses (
        qp_code TEXT PRIMARY KEY,
        qp_name TEXT NOT NULL,
        sector TEXT NOT NULL,
        nsqf_level INTEGER NOT NULL,
        entry_req TEXT NOT NULL,
        training_hours INTEGER NOT NULL,
        is_enterprise INTEGER DEFAULT 0,
        description TEXT NOT NULL,
        features_json TEXT NOT NULL
    );
    """)

    # Training Centers Master
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS training_centers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        qp_code TEXT NOT NULL,
        partner_type TEXT NOT NULL,
        district TEXT NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        FOREIGN KEY (qp_code) REFERENCES nsqf_courses(qp_code)
    );
    """)

    # District Perspective Heatmap Clusters
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS district_clusters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        block_name TEXT NOT NULL,
        sc_population_pct REAL NOT NULL,
        primary_traditional_craft TEXT NOT NULL,
        identified_skill_gap TEXT NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL
    );
    """)

    conn.commit()
    seed_nsqf_data(conn)
    seed_district_clusters(conn)
    conn.close()

def seed_nsqf_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM nsqf_courses;")
    if cursor.fetchone()[0] > 0:
        return

    sample_courses = [
        (
            "AGR/Q1101",
            "Micro Irrigation Technician",
            "Agriculture & FoodTech",
            4,
            "10th Class",
            360,
            0,
            "Installation, operation, and maintenance of micro-irrigation systems, drip lines, and solar pumps for rural farms.",
            json.dumps(["agriculture", "irrigation", "farming", "pumps", "water", "pipe", "tillage", "rural", "खेती", "सिंचाई", "पंप"])
        ),
        (
            "LSS/Q2301",
            "Leather Goods & Footwear Artisan",
            "Leather & Footwear",
            3,
            "5th Class",
            400,
            1,
            "Processing, cutting, stitching, and crafting of leather goods, traditional/modern footwear, and repair.",
            json.dumps(["leather", "cobbler", "shoes", "stitching", "cutting", "craft", "footwear", "traditional", "चमड़ा", "जूता", "मोची"])
        ),
        (
            "AMH/Q1010",
            "Self-Employed Tailor & Apparel Crafter",
            "Apparel & Handicrafts",
            4,
            "8th Class",
            390,
            1,
            "Garment construction, measuring, cutting, sewing machine maintenance, design customization, and rural retail boutique.",
            json.dumps(["tailor", "stitching", "sewing", "cloth", "garment", "apparel", "embroidery", "boutique", "सिलाई", "दर्जी", "कपड़ा"])
        ),
        (
            "ELE/Q1401",
            "Field Technician - Home Appliances & Solar Systems",
            "Electronics & Renewable Energy",
            4,
            "10th Class or ITI",
            420,
            0,
            "Maintenance, electrical testing, and installation of domestic wiring, solar home lighting, and inverter units.",
            json.dumps(["electrician", "wire", "switch", "motor", "solar", "appliance", "repair", "electrical", "बिजली", "वायरिंग", "पंखे"])
        ),
        (
            "CON/Q0102",
            "Assistant Mason & Concrete Construction Technician",
            "Construction & Infra",
            2,
            "None",
            300,
            0,
            "Foundational civil bricklaying, plastering, mortar preparation, curing, and structural masonry work.",
            json.dumps(["mason", "construction", "brick", "cement", "building", "plaster", "concrete", "labor", "राजमिस्त्री", "मजदूरी", "मिस्त्री"])
        ),
        (
            "AGR/Q4902",
            "Organic Fertilizer & Vermicompost Entrepreneur",
            "Agriculture & FoodTech",
            4,
            "8th Class",
            350,
            1,
            "Preparation of bio-fertilizers, vermicompost units, organic crop care, and rural agricultural sales cooperatives.",
            json.dumps(["organic", "fertilizer", "manure", "farming", "crops", "agriculture", "vermicompost", "soil", "खाद", "वर्मीकंपोस्ट", "गोबर", "खेती"])
        ),
        (
            "SSC/Q2212",
            "Domestic Data Entry Operator (DDEO)",
            "IT-ITeS & Digital Services",
            4,
            "10th Class",
            400,
            0,
            "Alphanumeric data processing, digital governance records transcription, and village CSC operations.",
            json.dumps(["computer", "data entry", "typing", "office", "csc", "digital", "कंप्यूटर", "डाटा एंट्री"])
        ),
        (
            "HCS/Q8702",
            "General Duty Assistant (Healthcare)",
            "Healthcare & Allied Services",
            4,
            "10th Class",
            480,
            0,
            "Patient care assistance, basic vitals monitoring, hospital hygiene maintenance, and rural PHC support.",
            json.dumps(["hospital", "patient", "nurse", "health", "clinic", "phc", "medical", "अस्पताल", "मरीज", "इलाज"])
        ),
        (
            "FIC/Q0103",
            "Traditional Food Products & Pickle Processing Technician",
            "Food Processing",
            3,
            "5th Class",
            320,
            1,
            "Processing, quality preservation, packaging, and commercial retail of regional spices, pickles, and dry food items.",
            json.dumps(["food", "pickle", "spices", "preservation", "kitchen", "snack", "अचार", "मसाले", "खाद्य", "पापड़"])
        )
    ]

    cursor.executemany("""
    INSERT INTO nsqf_courses (qp_code, qp_name, sector, nsqf_level, entry_req, training_hours, is_enterprise, description, features_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, sample_courses)

    sample_centers = [
        ("PMKK Skill Center - Hub 1", "AGR/Q1101", "Pradhan Mantri Kaushal Kendra", "Bhopal", 23.2620, 77.4100),
        ("RSETI Rural Enterprise Center", "LSS/Q2301", "Rural Self Employment Training Institute", "Bhopal", 23.2850, 77.3950),
        ("State SC Welfare Skill Training Cell", "AMH/Q1010", "State SC Corporation Training Wing", "Bhopal", 23.2400, 77.4200),
        ("Jan Shikshan Sansthan (JSS)", "ELE/Q1401", "National Skill Development Partner", "Bhopal", 23.2100, 77.4500),
        ("District Rural Polytechnic", "CON/Q0102", "Government ITI Affiliate", "Bhopal", 23.2700, 77.3700),
        ("Krishi Vigyan Kendra (KVK)", "AGR/Q4902", "ICAR Affiliated Center", "Bhopal", 23.3100, 77.4300),
        ("District CSC Training Hub", "SSC/Q2212", "State IT Mission Partner", "Bhopal", 23.2500, 77.4000),
        ("Red Cross Allied Health Center", "HCS/Q8702", "Healthcare Sector Skill Council", "Bhopal", 23.2200, 77.4300),
        ("RSETI Agro-Food Processing Lab", "FIC/Q0103", "Rural Self Employment Training Institute", "Bhopal", 23.2800, 77.3800)
    ]

    cursor.executemany("""
    INSERT INTO training_centers (name, qp_code, partner_type, district, lat, lon)
    VALUES (?, ?, ?, ?, ?, ?);
    """, sample_centers)

    conn.commit()

def seed_district_clusters(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM district_clusters;")
    if cursor.fetchone()[0] > 0:
        return

    clusters = [
        ("Phanda Urban Cluster", 24.5, "Leather & Footwear", "Modern machine stitching gap", 23.2620, 77.4100),
        ("Berasia Rural Block", 31.8, "Agriculture & Dairy", "Micro-irrigation & cold storage tech", 23.6333, 77.4333),
        ("Govindpura Industrial Perimeter", 28.2, "Electrical & Solar", "Solar rooftop technician deficit", 23.2400, 77.4500),
        ("Kolar Craft Belt", 22.1, "Apparel & Tailoring", "Export grade garment finishing", 23.1800, 77.4200),
        ("Huzur Peri-Urban Belt", 26.4, "Food Processing & Micro-Enterprise", "Standard packaging & food safety compliance", 23.3200, 77.3500)
    ]

    cursor.executemany("""
    INSERT INTO district_clusters (block_name, sc_population_pct, primary_traditional_craft, identified_skill_gap, lat, lon)
    VALUES (?, ?, ?, ?, ?, ?);
    """, clusters)
    conn.commit()