# db/seed.py
"""
SpecSense AI — Database Seed Script

Populates all reference/lookup tables from hardcoded values found across:
  - OCR_Reader/src/extraction.py (regex patterns, preprocessing rules, corrections)
  - OCR_Reader/src/validation.py (validation rules, materials, IEC sizes)
  - Keyword_Generator/keyword_tool.py (keyword patterns, categories)
  - Vision_Model/config/settings.py (vision config, diameter rules)
  - Vision_Model/Cable_Dataset/classes.txt.txt (detection classes)

Run once after creating tables:
    python -m db.seed
"""

from db.database import SessionLocal, engine
from db.models import Base
from db.crud import (
    # Extraction
    create_extraction_pattern, create_preprocessing_rule,
    # Correction
    create_correction_rule,
    # Cable Spec
    create_cable_type, create_standard,
    # Validation
    create_validation_rule, create_validation_rule_parameter,
    create_material_whitelist, create_iec_standard_size,
    # Keywords
    create_keyword_pattern, create_cable_category, create_category_keyword,
    # Vision
    create_detection_class,
    # Config
    create_model_version, create_vision_config_param, create_diameter_spec_rule,
)


def seed_all():
    db = SessionLocal()

    try:
        print("=" * 60)
        print("SpecSense AI — Seeding Database")
        print("=" * 60)

        # 1. EXTRACTION PATTERNS
        # Source: OCR_Reader/src/extraction.py — SpecificationExtractor.patterns
        
        print("\n[1/10] Seeding extraction patterns...")

        extraction_patterns = [
            ("cable_type", r"\b(C[o0]pp[\s]*[e3]r|Cu|Aluminium|Aluminum|Al)\b\s*(?:C[@a]ble|Conductor)?",
             "Cable conductor material — handles OCR corruptions like C0pp3r"),
            ("voltage", r"(\d[\d\s\.]*[/]?[\d\sS]*\s*[kK]?[vV])",
             "Voltage rating — handles 450/750V, 0.6/1kV with OCR noise"),
            ("current_rating", r"(\d[\d\s]*\s*(?:Amps?|A)\b)",
             "Current rating in Amps"),
            ("insulation", r"(XLPE|PVC)",
             "Insulation material type"),
            ("conductor_count", r"(\d+)\s*(?:Core|Cores|x)",
             "Number of conductors/cores"),
            ("conductor_size", r"(\d+(?:[\s]*[xX][\s]*\d+)?[\s]*m[\s]*m[h]?[\s]*[2²\?]?)",
             "Conductor cross-section area in mm² — handles OCR spacing like '6m m 2'"),
            ("sheath", r"(PVC|HDPE|LDPE|Lead|LAZH|LSOH|MDPE|EPR|PUR|TPU|Neoprene|Rubber|LSZH)\s*(?:Sheath|Jacket)?",
             "Sheath/jacket material"),
            ("operating_temperature", r"(\d+(?:[\s]*[O0\d]+)?[\s]*(?:°|\*|deg|degrees)?[\s]*C)",
             "Operating temperature — handles OCR '4O C' as '40°C'"),
            ("insulation_resistance", r"(\d+[\s]*M?[O\u03a9][\s]*[\.]?k?m)",
             "Insulation resistance — handles OCR reading Ω as O"),
            ("armor", r"(Stee[l1][\s]*[WT][l1Iae3p]+[\s]*Armo[r0x]|\bSWA\b|\bSTA\b|SWA|AWA|ATA|GSWA|GSTA|CWA|BWA)",
             "Armor type — handles Steel Wire/Tape Armor and abbreviations"),
        ]

        for field_name, pattern, desc in extraction_patterns:
            create_extraction_pattern(db, field_name=field_name, regex_pattern=pattern, description=desc)
        print(f"  ✓ {len(extraction_patterns)} extraction patterns seeded")

        
        # 2. PREPROCESSING RULES
        # Source: OCR_Reader/src/extraction.py — SpecificationExtractor.preprocess_text()
        print("\n[2/10] Seeding preprocessing rules...")

        preprocessing_rules = [
            # Word fixes (order matters!)
            ("word_fix", r"C[@a]b[l1][e3]", "Cable", "IGNORECASE", "Fix corrupted 'Cable'", 1),
            ("word_fix", r"V[0o]ltage", "Voltage", "IGNORECASE", "Fix corrupted 'Voltage'", 2),
            ("word_fix", r"C[ou]rr[e3]nt", "Current", "IGNORECASE", "Fix corrupted 'Current'", 3),
            ("word_fix", r"R[@a]t[i1]ng", "Rating", "IGNORECASE", "Fix corrupted 'Rating'", 4),
            ("word_fix", r"Insu[l1]at[i1][0o]n", "Insulation", "IGNORECASE", "Fix corrupted 'Insulation'", 5),
            ("word_fix", r"C[0o]ndu[\s]*ct[0o]r", "Conductor", "IGNORECASE", "Fix corrupted 'Conductor'", 6),
            ("word_fix", r"Sh[e3]ath", "Sheath", "IGNORECASE", "Fix corrupted 'Sheath'", 7),
            ("word_fix", r"Arm[0o]r", "Armor", "IGNORECASE", "Fix corrupted 'Armor'", 8),
            ("word_fix", r"[0o]p[e3]rat[i1]ng", "Operating", "IGNORECASE", "Fix corrupted 'Operating'", 9),
            ("word_fix", r"T[e3]mp[\s]*[e3]ratur[e3]", "Temperature", "IGNORECASE", "Fix corrupted 'Temperature'", 10),
            ("word_fix", r"R[e3]s[i1]stanc[e3]", "Resistance", "IGNORECASE", "Fix corrupted 'Resistance'", 11),
            ("word_fix", r"C[0o]pp[\s]*[e3]r", "Copper", "IGNORECASE", "Fix corrupted 'Copper'", 12),
            ("word_fix", r"P[0o]w[e3]r", "Power", "IGNORECASE", "Fix corrupted 'Power'", 13),
            ("word_fix", r"c[0o]r[e3]s?", "cores", "IGNORECASE", "Fix corrupted 'cores'", 14),
            ("word_fix", r"St[e3][e3][l1]", "Steel", "IGNORECASE", "Fix corrupted 'Steel'", 15),
            ("word_fix", r"W[i1]r[e3]", "Wire", "IGNORECASE", "Fix corrupted 'Wire'", 16),
            # Number fixes
            ("number_fix", r"(\d)O(\d)", r"\g<1>0\2", "", "Fix O→0 in numbers (digit-O-digit)", 17),
            ("number_fix", r"(\d)S(\d)", r"\g<1>5\2", "", "Fix S→5 in numbers (digit-S-digit)", 18),
            ("number_fix", r"(\d)O\s*V", r"\g<1>0 V", "", "Fix O→0 before V", 19),
            ("number_fix", r"(\d)S\s*V", r"\g<1>5 V", "", "Fix S→5 before V", 20),
            ("number_fix", r"O(\d)", r"0\1", "", "Fix leading O→0", 21),
            ("number_fix", r"S(\d)", r"5\1", "", "Fix leading S→5", 22),
            # Space fixes
            ("space_fix", r"(\d)\s+(\d)\s*A\b", r"\1\2A", "", "Fix spaced numbers before A (3 2 A → 32A)", 23),
        ]

        for rule_type, search, replace, flags, desc, order in preprocessing_rules:
            create_preprocessing_rule(
                db, rule_type=rule_type, search_regex=search,
                replacement=replace, flags=flags, description=desc,
                execution_order=order
            )
        print(f"  ✓ {len(preprocessing_rules)} preprocessing rules seeded")

        # ─────────────────────────────────────────────
        # 3. CORRECTION RULES
        # Source: OCR_Reader/src/extraction.py — SpecCorrector
        # ─────────────────────────────────────────────
        print("\n[3/10] Seeding correction rules...")

        correction_rules = [
            # Armor abbreviation expansions
            ("armor", "abbreviation_expand", "AWA", "Aluminum Wire Armor", None, None, "AWA → Aluminum Wire Armor"),
            ("armor", "abbreviation_expand", "SWA", "Steel Wire Armor", None, None, "SWA → Steel Wire Armor"),
            ("armor", "abbreviation_expand", "STA", "Steel Tape Armor", None, None, "STA → Steel Tape Armor"),
            ("armor", "abbreviation_expand", "ATA", "Aluminum Tape Armor", None, None, "ATA → Aluminum Tape Armor"),
            ("armor", "abbreviation_expand", "GSWA", "Galvanized Steel Wire Armor", None, None, "GSWA → Galvanized Steel Wire Armor"),
            ("armor", "abbreviation_expand", "GSTA", "Galvanized Steel Tape Armor", None, None, "GSTA → Galvanized Steel Tape Armor"),
            ("armor", "abbreviation_expand", "CWA", "Copper Wire Armor", None, None, "CWA → Copper Wire Armor"),
            ("armor", "abbreviation_expand", "BWA", "Braided Wire Armor", None, None, "BWA → Braided Wire Armor"),
            # Voltage corrections
            ("voltage", "unit_format", None, None, r"(\d)(k?V)", r"\1 \2", "Normalize spacing: 0.6/1kV → 0.6/1 kV"),
            # Temperature corrections
            ("operating_temperature", "heuristic_repair", None, None, None, None, "Single digit 3-9 followed by 'c' → assume missing zero (e.g. 4c → 40°C)"),
            ("operating_temperature", "unit_format", None, None, r"(\d+)\s*[cCx]?\.?$", r"\1°C", "Standardize C to °C"),
            # Resistance corrections
            ("insulation_resistance", "unit_format", None, None, r"(\d)(MΩ)", r"\1 \2", "Add space before MΩ"),
            # Conductor size corrections
            ("conductor_size", "regex_transform", None, None, None, None, "NxS pattern split: 4x16mm² → cores=4, size=16mm²"),
            ("conductor_size", "unit_format", None, None, None, None, "mh→mm, ?→2, append 2 if missing after mm"),
        ]

        for field, rtype, abbrev, expanded, regex, repl, desc in correction_rules:
            create_correction_rule(
                db, field_name=field, rule_type=rtype,
                abbreviation=abbrev, expanded_value=expanded,
                search_regex=regex, replacement=repl, description=desc
            )
        print(f"  ✓ {len(correction_rules)} correction rules seeded")

        # ─────────────────────────────────────────────
        # 4. CABLE TYPES & STANDARDS
        # ─────────────────────────────────────────────
        print("\n[4/10] Seeding cable types & standards...")

        cable_types = [
            ("Copper", "Copper conductor cable"),
            ("Aluminum", "Aluminum conductor cable"),
            ("Copper Control", "Copper control cable"),
            ("Heavy Duty Power Feeder", "High-capacity power feeder cable"),
            ("Power Cable (Armoured)", "Armoured power cable"),
            ("Control/Light Duty", "Light duty control cable"),
        ]
        for name, desc in cable_types:
            create_cable_type(db, type_name=name, description=desc)

        standards = [
            ("IEC 60502-1", "Power cables with extruded insulation and their accessories for rated voltages from 1 kV up to 30 kV", "2019"),
            ("IEC 60227", "PVC insulated cables of rated voltages up to and including 450/750 V", "2019"),
            ("IEC 60228", "Conductors of insulated cables (standard conductor classes and sizes)", "2023"),
            ("IEC 60332", "Tests on electric cables under fire conditions", "2019"),
            ("BS 5467", "British Standard for XLPE insulated cables", "1997"),
            ("BS 6724", "British Standard for LSZH cables", "2016"),
        ]
        for name, desc, ver in standards:
            create_standard(db, standard_name=name, description=desc, version=ver)

        print(f"  ✓ {len(cable_types)} cable types, {len(standards)} standards seeded")

        # ─────────────────────────────────────────────
        # 5. VALIDATION RULES
        # Source: OCR_Reader/src/validation.py — CableValidator (11 rules)
        # ─────────────────────────────────────────────
        print("\n[5/10] Seeding validation rules...")

        validation_rules_data = [
            ("R1", "Cable Type Validation", "Reject hybrid Fiber-Optic/Power cables; flag unknown/ambiguous types", "error"),
            ("R2", "Voltage Rating Validation", "Reject mixed AC/DC ratings and extreme voltage ratios (>50x)", "error"),
            ("R3", "Current vs Conductor Size", "Reject unrealistic current density (must be 0.1-30 A/mm²)", "error"),
            ("R4", "Insulation Material Validation", "Reject non-electrical materials (PLASTIC, FOAM, GLASS, etc.)", "error"),
            ("R5", "Conductor Count Validation", "Reject fractional conductor counts", "error"),
            ("R7", "Armor Material Validation", "Reject non-metallic armor materials", "error"),
            ("R8", "Operating Temperature Range", "Temperature must be within -40°C to 105°C", "error"),
            ("R9", "IEC Standard Cross-Section", "Conductor size must be a standard IEC cross-section (±5%)", "warning"),
            ("R10", "Conductor Size Realism", "Reject unrealistic conductor sizes (<0.1 mm²)", "error"),
            ("R11", "Material-Voltage Compatibility", "PVC insulation cannot be used for High Voltage (>3.3kV); HV requires verified insulation", "error"),
            ("R12", "High Voltage Safety", "Voltage >1000V requires verified insulation type — cannot be None/Unknown", "error"),
        ]

        for code, name, desc, severity in validation_rules_data:
            rule = create_validation_rule(
                db, rule_code=code, rule_name=name,
                description=desc, severity=severity
            )
            # Add parameters per rule
            if code == "R3":
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="min_density", param_value="0.1", value_type="float", description="Minimum current density A/mm²")
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="max_density", param_value="30", value_type="float", description="Maximum current density A/mm²")
            elif code == "R8":
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="min_temp", param_value="-40", value_type="int", description="Minimum operating temperature °C")
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="max_temp", param_value="105", value_type="int", description="Maximum operating temperature °C")
            elif code == "R9":
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="tolerance_pct", param_value="5", value_type="float", description="Allowed deviation from IEC standard size (%)")
            elif code == "R10":
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="min_size", param_value="0.1", value_type="float", description="Minimum realistic conductor size mm²")
            elif code == "R11":
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="max_pvc_voltage", param_value="3300", value_type="float", description="Maximum voltage for PVC insulation (V)")
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="required_insulation_above", param_value="XLPE", value_type="string", description="Required insulation above PVC voltage limit")
            elif code == "R12":
                create_validation_rule_parameter(db, rule_id=rule.rule_id, param_key="hv_threshold", param_value="1000", value_type="float", description="Voltage threshold requiring verified insulation (V)")

        print(f"  ✓ {len(validation_rules_data)} validation rules with parameters seeded")

        # ─────────────────────────────────────────────
        # 6. MATERIAL WHITELISTS
        # Source: OCR_Reader/src/validation.py — CableValidator.rules
        # ─────────────────────────────────────────────
        print("\n[6/10] Seeding material whitelists...")

        material_entries = [
            # Valid insulation
            ("insulation_valid", "PVC", "Polyvinyl Chloride"),
            ("insulation_valid", "XLPE", "Cross-linked Polyethylene"),
            ("insulation_valid", "EPR", "Ethylene Propylene Rubber"),
            ("insulation_valid", "RUBBER", "Natural/Synthetic Rubber"),
            ("insulation_valid", "LSZH", "Low Smoke Zero Halogen"),
            # Valid sheath
            ("sheath_valid", "PVC", "Polyvinyl Chloride"),
            ("sheath_valid", "PE", "Polyethylene (generic)"),
            ("sheath_valid", "LSZH", "Low Smoke Zero Halogen"),
            ("sheath_valid", "RUBBER", "Natural/Synthetic Rubber"),
            ("sheath_valid", "HDPE", "High Density Polyethylene"),
            ("sheath_valid", "MDPE", "Medium Density Polyethylene"),
            ("sheath_valid", "LDPE", "Low Density Polyethylene"),
            # Valid armor
            ("armor_valid", "STEEL", "Steel armor"),
            ("armor_valid", "ALUMINUM", "Aluminum armor"),
            ("armor_valid", "COPPER", "Copper armor"),
            ("armor_valid", "SWA", "Steel Wire Armor"),
            ("armor_valid", "STA", "Steel Tape Armor"),
            ("armor_valid", "AWA", "Aluminum Wire Armor"),
            ("armor_valid", "ATA", "Aluminum Tape Armor"),
            ("armor_valid", "NONE", "No armor / Unarmored"),
            # Invalid materials
            ("invalid", "PLASTIC", "Generic plastic — not an electrical material"),
            ("invalid", "FOAM", "Foam — not an electrical material"),
            ("invalid", "GLASS", "Glass — not an electrical material"),
            ("invalid", "WOOD", "Wood — not an electrical material"),
            ("invalid", "PAPER", "Paper — not an electrical material (legacy excepted)"),
            ("invalid", "PAINT", "Paint — not an electrical material"),
            ("invalid", "WATER", "Water — not an electrical material"),
            ("invalid", "STONE", "Stone — not an electrical material"),
        ]

        for category, name, desc in material_entries:
            create_material_whitelist(db, category=category, material_name=name, description=desc)

        print(f"  ✓ {len(material_entries)} material entries seeded")

        # IEC Standard Sizes
        # Source: validation.py — standard_sizes
        iec_sizes = [0.5, 0.75, 1.0, 1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0, 70.0,
                     95.0, 120.0, 150.0, 185.0, 240.0, 300.0, 400.0, 500.0, 630.0, 800.0, 1000.0]
        for size in iec_sizes:
            create_iec_standard_size(db, size_mm2=size)

        print(f"  ✓ {len(iec_sizes)} IEC standard sizes seeded")

        # ─────────────────────────────────────────────
        # 7. KEYWORD PATTERNS
        # Source: Keyword_Generator/keyword_tool.py — KeywordExtractor.patterns
        # ─────────────────────────────────────────────
        print("\n[7/10] Seeding keyword patterns...")

        keyword_patterns_data = [
            ("Voltage", r"\b\d+(?:[.,/]\d+)*\s*k?V\b", "Voltage values with optional ranges"),
            ("Current", r"\b\d+(?:\.\d+)?\s*A\b", "Current rating in Amps"),
            ("CrossSection", r"\b\d+(?:\.\d+)?\s*mm2\b", "Cross-section area in mm²"),
            ("Cores", r"\b(?<![-+])\d{1,2}C\b|\b\d+\s*Core\b", "Core count patterns (3C, 4 Core)"),
            ("Material", r"\b(Copper|Aluminum|XLPE|PVC|SWA|AWA)\b", "Key material names"),
            ("Conductor Type", r"\b(ACSR|AAAC|AAC|HTSL)\b", "Overhead conductor type designations"),
        ]

        for label, pattern, desc in keyword_patterns_data:
            create_keyword_pattern(db, label=label, regex_pattern=pattern, description=desc)

        print(f"  ✓ {len(keyword_patterns_data)} keyword patterns seeded")

        # ─────────────────────────────────────────────
        # 8. CABLE CATEGORIES
        # Source: Keyword_Generator/keyword_tool.py — CableClassifier.categories
        # ─────────────────────────────────────────────
        print("\n[8/10] Seeding cable categories & keywords...")

        categories_data = [
            ("HTLS Conductors", None, None, 5, "High Temperature Low Sag conductors",
             ["htls", "htsl", "high temperature low sag", "accc", "acss", "tacsr", "stacir", "gap type", "invar"]),
            ("Overhead Conductors", None, None, 4, "Overhead bare/bundled conductors",
             ["overhead", "bare copper", "aac", "aaac", "acsr", "abc", "areal bundled", "transmission line"]),
            ("High & Extra High Voltage Cables", 30001, 500000, 3, "HV/EHV cables (30kV-500kV)",
             ["high voltage", "extra high voltage", "ehv", "hv cable", "66kv", "132kv", "220kv", "400kv", "500kv"]),
            ("Medium Voltage Cables", 3001, 30000, 2, "MV cables (3.3kV-30kV)",
             ["medium voltage", "mv cable", "6.6kv", "11kv", "22kv", "33kv"]),
            ("Low Voltage Cables", 0, 3000, 1, "LV cables (up to 3kV)",
             ["low voltage", "lv cable", "0.6/1kv", "1.8/3kv", "pvc insulated"]),
        ]

        for cat_name, v_min, v_max, priority, desc, keywords in categories_data:
            cat = create_cable_category(
                db, category_name=cat_name,
                voltage_min_v=v_min, voltage_max_v=v_max,
                priority=priority, description=desc
            )
            for kw in keywords:
                create_category_keyword(db, category_id=cat.category_id, keyword=kw)

        print(f"  ✓ {len(categories_data)} categories with keywords seeded")

        # ─────────────────────────────────────────────
        # 9. VISION CONFIG & DETECTION CLASSES
        # Source: Vision_Model/config/settings.py & classes.txt.txt
        # ─────────────────────────────────────────────
        print("\n[9/10] Seeding vision config & detection classes...")

        # Detection classes from classes.txt.txt
        detection_classes = [
            ("Conductor", "Central conductor element in cable cross-section"),
            ("Insulation", "Insulation layer around conductor"),
            ("Sheath_Jacket", "Outer sheath/jacket layer"),
            ("Filler", "Filler material between cable elements"),
            ("Armour", "Armor/protection layer"),
        ]
        for name, desc in detection_classes:
            create_detection_class(db, class_name=name, description=desc)

        # Vision config params
        vision_params = [
            ("PIXELS_PER_MM", "18.5", "float", "Calibration: pixels per millimeter"),
            ("CONF_THRESHOLD", "0.01", "float", "Minimum YOLO detection confidence threshold"),
            ("QC_MIN_DIAMETER_MM", "5.0", "float", "Minimum cable diameter for QC PASS (mm)"),
            ("ZOOM_FACTOR", "2.0", "float", "PDF to image conversion zoom factor"),
        ]
        for key, val, vtype, desc in vision_params:
            create_vision_config_param(db, param_key=key, param_value=val, value_type=vtype, description=desc)

        # Diameter-to-spec rules
        # Source: settings.py — get_cable_specs()
        diameter_rules = [
            (40.0, 9999.0, "Medium Voltage (11 kV - 33 kV)", "Class 2 (Compacted Copper/Al)",
             "XLPE + Semi-conductive Layer", "HDPE / PVC (Red/Black)", "Heavy Duty Power Feeder", 3),
            (15.0, 40.0, "Low Voltage (0.6/1 kV)", "Class 2 (Stranded Copper)",
             "XLPE (Cross-linked PE)", "PVC (Black/UV Resistant)", "Power Cable (Armoured)", 2),
            (0.0, 15.0, "Low Voltage (300/500 V)", "Class 1 (Solid Copper)",
             "PVC (Polyvinyl Chloride)", "PVC (Grey/White)", "Control/Light Duty", 1),
        ]
        for min_d, max_d, volt, cond, insul, sheath, ctype, pri in diameter_rules:
            create_diameter_spec_rule(
                db, min_diameter_mm=min_d, max_diameter_mm=max_d,
                voltage_class=volt, conductor_class=cond,
                insulation_type=insul, sheath_material=sheath,
                cable_type=ctype, priority=pri
            )

        # Model versions
        create_model_version(
            db, model_type="yolo", model_name="YOLOv8m-seg", version_tag="v1.0",
            framework="ultralytics", description="Cable cross-section segmentation model"
        )
        create_model_version(
            db, model_type="ocr", model_name="EasyOCR", version_tag="v1.0",
            framework="easyocr", description="Text recognition engine"
        )
        create_model_version(
            db, model_type="spacy", model_name="en_core_web_sm", version_tag="v1.0",
            framework="spacy", description="SpaCy NER model for spec extraction"
        )

        print(f"  ✓ {len(detection_classes)} detection classes, {len(vision_params)} config params, {len(diameter_rules)} diameter rules, 3 model versions seeded")

        # ─────────────────────────────────────────────
        # 10. ADMIN USER
        # ─────────────────────────────────────────────
        print("\n[10/10] Seeding default admin user...")
        from db.crud import get_user_by_email
        if not get_user_by_email(db, "admin@specsense.ai"):
            from db.crud import create_user
            create_user(db, full_name="Admin", email="admin@specsense.ai", role="admin")
            print("  ✓ Default admin user created")
        else:
            print("  ⊘ Admin user already exists, skipping")

        print("\n" + "=" * 60)
        print("✅ Database seeding complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Seeding error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Create all tables first
    Base.metadata.create_all(bind=engine)
    print("Tables created/verified.")
    # Then seed
    seed_all()
