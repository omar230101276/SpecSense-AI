# db/models.py
"""
SpecSense AI — Complete Database Schema
========================================
Covers: Users, Documents, OCR Pipeline, Extraction Patterns,
Correction Rules, Cable Specifications, Validation Engine,
Keyword Generation, Vision Inspection, Model Config, Training.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float,
    ForeignKey, TIMESTAMP, JSON, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from db.database import Base


# ═══════════════════════════════════════════════════════════════════
# 1. USER & AUTH
# ═══════════════════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    role = Column(String(20), default="viewer")  # admin / engineer / viewer
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    documents = relationship("Document", back_populates="uploader")
    validation_reviews = relationship("ValidationHistory", back_populates="reviewer")


# ═══════════════════════════════════════════════════════════════════
# 2. DOCUMENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

class Document(Base):
    __tablename__ = "documents"

    doc_id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, png, jpg, docx
    file_size_kb = Column(Float)
    file_hash = Column(String(64))  # SHA-256 for dedup
    page_count = Column(Integer)
    upload_date = Column(TIMESTAMP, server_default="now()")
    uploaded_by = Column(Integer, ForeignKey("users.user_id"))
    status = Column(String(20), default="uploaded")  # uploaded / processing / processed / failed

    # Relationships
    uploader = relationship("User", back_populates="documents")
    ocr_sessions = relationship("OCRSession", back_populates="document")
    cable_specs = relationship("CableSpec", back_populates="document")
    inspections = relationship("Inspection", back_populates="document")


# ═══════════════════════════════════════════════════════════════════
# 3. OCR PIPELINE
# ═══════════════════════════════════════════════════════════════════

class OCRSession(Base):
    """Tracks each OCR processing run on a document."""
    __tablename__ = "ocr_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.doc_id"), nullable=False)
    languages = Column(String(50), default="en")  # comma-separated: "en,ar"
    gpu_enabled = Column(Boolean, default=True)
    total_pages = Column(Integer)
    total_chars = Column(Integer)
    processing_time_ms = Column(Integer)
    status = Column(String(20), default="running")  # running / completed / failed
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    document = relationship("Document", back_populates="ocr_sessions")
    page_results = relationship("OCRPageResult", back_populates="session")
    extraction_run = relationship("ExtractionRun", back_populates="ocr_session", uselist=False)


class OCRPageResult(Base):
    """Raw OCR text output per page."""
    __tablename__ = "ocr_page_results"

    page_result_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("ocr_sessions.session_id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text)
    confidence_avg = Column(Float)
    word_count = Column(Integer)
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    session = relationship("OCRSession", back_populates="page_results")


# ═══════════════════════════════════════════════════════════════════
# 4. EXTRACTION PATTERNS (Configurable Regex)
# ═══════════════════════════════════════════════════════════════════

class ExtractionPattern(Base):
    """Regex patterns for cable specification field extraction.
    Source: OCR_Reader/src/extraction.py — SpecificationExtractor.patterns
    """
    __tablename__ = "extraction_patterns"

    pattern_id = Column(Integer, primary_key=True)
    field_name = Column(String(50), nullable=False)  # cable_type, voltage, insulation, etc.
    language = Column(String(5), default="en")
    regex_pattern = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher = tried first
    created_at = Column(TIMESTAMP, server_default="now()")
    updated_at = Column(TIMESTAMP, server_default="now()")

    __table_args__ = (
        UniqueConstraint("field_name", "language", "priority", name="uq_pattern_field_lang_pri"),
    )


class PreprocessingRule(Base):
    """OCR text preprocessing/correction regex rules applied before extraction.
    Source: OCR_Reader/src/extraction.py — SpecificationExtractor.preprocess_text()
    """
    __tablename__ = "preprocessing_rules"

    rule_id = Column(Integer, primary_key=True)
    rule_type = Column(String(30), nullable=False)  # word_fix, number_fix, space_fix
    search_regex = Column(Text, nullable=False)
    replacement = Column(Text, nullable=False)
    flags = Column(String(20), default="IGNORECASE")  # regex flags
    description = Column(Text)
    execution_order = Column(Integer, default=0)  # Order matters for regex chains
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default="now()")


# ═══════════════════════════════════════════════════════════════════
# 5. CORRECTION RULES & AUDIT
# ═══════════════════════════════════════════════════════════════════

class CorrectionRule(Base):
    """Post-OCR field correction rules and mappings.
    Source: OCR_Reader/src/extraction.py — SpecCorrector
    """
    __tablename__ = "correction_rules"

    rule_id = Column(Integer, primary_key=True)
    field_name = Column(String(50), nullable=False)  # voltage, temperature, armor, etc.
    rule_type = Column(String(30), nullable=False)  # abbreviation_expand, unit_format, heuristic_repair, regex_transform
    abbreviation = Column(String(50))  # e.g. "SWA"
    expanded_value = Column(String(100))  # e.g. "Steel Wire Armor"
    search_regex = Column(Text)  # For regex-based corrections
    replacement = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default="now()")

    __table_args__ = (
        UniqueConstraint("field_name", "rule_type", "abbreviation", name="uq_correction_rule"),
    )


class ExtractionRun(Base):
    """Tracks a complete extraction+correction pipeline run."""
    __tablename__ = "extraction_runs"

    run_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("ocr_sessions.session_id"), nullable=False)
    raw_specs_json = Column(JSON)  # Specs before correction
    corrected_specs_json = Column(JSON)  # Specs after correction
    extraction_method = Column(String(20), default="regex")  # regex / spacy / hybrid
    total_fields_extracted = Column(Integer)
    total_corrections_applied = Column(Integer)
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    ocr_session = relationship("OCRSession", back_populates="extraction_run")
    corrections = relationship("CorrectionLog", back_populates="extraction_run")


class CorrectionLog(Base):
    """Audit trail of individual corrections applied during SpecCorrector.correct_all().
    Source: OCR_Reader/src/extraction.py — SpecCorrector.log()
    """
    __tablename__ = "correction_logs"

    log_id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("extraction_runs.run_id"), nullable=False)
    field_name = Column(String(50), nullable=False)
    original_value = Column(Text)
    corrected_value = Column(Text)
    reason = Column(String(100))  # Formatting, NxS Split, Expansion, Heuristic Repair, Unit Normalization
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    extraction_run = relationship("ExtractionRun", back_populates="corrections")


# ═══════════════════════════════════════════════════════════════════
# 6. CABLE SPECIFICATIONS (Core Business Entity)
# ═══════════════════════════════════════════════════════════════════

class CableType(Base):
    """Catalog of cable types."""
    __tablename__ = "cable_types"

    cable_type_id = Column(Integer, primary_key=True)
    type_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

    # Relationships
    specs = relationship("CableSpec", back_populates="cable_type")


class Standard(Base):
    """IEC / National standards catalog."""
    __tablename__ = "standards"

    standard_id = Column(Integer, primary_key=True)
    standard_name = Column(String(50), nullable=False)  # e.g. IEC 60502-1
    description = Column(Text)
    version = Column(String(20))

    # Relationships
    specs = relationship("CableSpec", back_populates="standard")
    standard_sizes = relationship("IECStandardSize", back_populates="standard")


class CableSpec(Base):
    """Extracted cable specification per document.
    Enhanced with all fields from extraction.py + validation.py.
    """
    __tablename__ = "cable_specs"

    spec_id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey("documents.doc_id"), nullable=False)
    cable_type_id = Column(Integer, ForeignKey("cable_types.cable_type_id"))
    standard_id = Column(Integer, ForeignKey("standards.standard_id"))
    run_id = Column(Integer, ForeignKey("extraction_runs.run_id"))  # Link to extraction run

    # --- All extracted specification fields ---
    voltage_rating = Column(String(50))
    current_rating = Column(String(30))
    conductor_material = Column(String(30))  # Copper / Aluminum
    conductor_class = Column(String(20))  # Class 1 (Solid), Class 2 (Stranded)
    insulation_type = Column(String(50))  # XLPE, PVC, EPR, RUBBER
    number_of_cores = Column(Integer)
    cross_section_area = Column(String(20))  # e.g. "16 mm²"
    armor_type = Column(String(50))  # Steel Wire Armor, SWA, etc.
    sheath_material = Column(String(30))  # PVC, LSZH, HDPE, etc.
    fire_performance = Column(String(50))
    operating_temperature = Column(String(20))
    insulation_resistance = Column(String(30))  # e.g. "100 MΩ·km"

    # --- Meta fields ---
    is_verified = Column(Boolean, default=False)
    extraction_confidence = Column(Float)
    extraction_method = Column(String(20), default="regex")  # regex / spacy / hybrid
    created_at = Column(TIMESTAMP, server_default="now()")

    # --- Cross-link: Link OCR spec to Vision inspection ---
    linked_inspection_id = Column(Integer, ForeignKey("inspections.id"))

    # Relationships
    document = relationship("Document", back_populates="cable_specs")
    cable_type = relationship("CableType", back_populates="specs")
    standard = relationship("Standard", back_populates="specs")
    extraction_run = relationship("ExtractionRun")
    linked_inspection = relationship("Inspection")
    keywords = relationship("Keyword", back_populates="spec")
    validation_results = relationship("ValidationResult", back_populates="spec")
    validation_history = relationship("ValidationHistory", back_populates="spec")
    spec_field_values = relationship("SpecFieldValue", back_populates="spec")


class SpecFieldValue(Base):
    """Individual field values with per-field confidence and source tracking.
    Enables granular provenance: which regex matched, confidence, page number.
    """
    __tablename__ = "spec_field_values"

    value_id = Column(Integer, primary_key=True)
    spec_id = Column(Integer, ForeignKey("cable_specs.spec_id"), nullable=False)
    field_name = Column(String(50), nullable=False)
    raw_value = Column(Text)  # Before correction
    corrected_value = Column(Text)  # After correction
    confidence = Column(Float)
    source = Column(String(20))  # regex / spacy / manual
    matched_pattern_id = Column(Integer, ForeignKey("extraction_patterns.pattern_id"))
    page_number = Column(Integer)
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    spec = relationship("CableSpec", back_populates="spec_field_values")
    matched_pattern = relationship("ExtractionPattern")


# ═══════════════════════════════════════════════════════════════════
# 7. VALIDATION ENGINE
# ═══════════════════════════════════════════════════════════════════

class ValidationRule(Base):
    """Configurable engineering validation rules.
    Source: OCR_Reader/src/validation.py — CableValidator (11 rules)
    """
    __tablename__ = "validation_rules"

    rule_id = Column(Integer, primary_key=True)
    rule_code = Column(String(10), nullable=False, unique=True)  # R1, R2, ... R11
    rule_name = Column(String(100), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="error")  # error / warning / info
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    parameters = relationship("ValidationRuleParameter", back_populates="rule")
    error_records = relationship("ValidationError", back_populates="rule")


class ValidationRuleParameter(Base):
    """Configurable parameters for each validation rule.
    Replaces hardcoded lists like valid_insulation, temp_range, standard_sizes.
    """
    __tablename__ = "validation_rule_parameters"

    param_id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey("validation_rules.rule_id"), nullable=False)
    param_key = Column(String(50), nullable=False)  # e.g. "valid_material", "min_value", "max_value"
    param_value = Column(Text, nullable=False)  # Value as string, parsed at runtime
    value_type = Column(String(20), default="string")  # string / float / int / list
    description = Column(Text)

    # Relationships
    rule = relationship("ValidationRule", back_populates="parameters")


class MaterialWhitelist(Base):
    """Valid and invalid materials for insulation, sheath, armor.
    Source: validation.py — CableValidator.rules
    """
    __tablename__ = "material_whitelists"

    material_id = Column(Integer, primary_key=True)
    category = Column(String(30), nullable=False)  # insulation_valid, sheath_valid, armor_valid, invalid
    material_name = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("category", "material_name", name="uq_material_cat_name"),
    )


class IECStandardSize(Base):
    """IEC standard cross-section sizes.
    Source: validation.py — standard_sizes list (24 values)
    """
    __tablename__ = "iec_standard_sizes"

    size_id = Column(Integer, primary_key=True)
    standard_id = Column(Integer, ForeignKey("standards.standard_id"))
    size_mm2 = Column(Float, nullable=False, unique=True)
    tolerance_pct = Column(Float, default=5.0)  # 5% tolerance from validation logic
    description = Column(Text)

    # Relationships
    standard = relationship("Standard", back_populates="standard_sizes")


class ValidationResult(Base):
    """Overall validation outcome per cable spec.
    Source: CableValidator.validate_cable() return dict
    """
    __tablename__ = "validation_results"

    validation_id = Column(Integer, primary_key=True)
    spec_id = Column(Integer, ForeignKey("cable_specs.spec_id"), nullable=False)
    status = Column(String(20), nullable=False)  # READY / NOT READY / UNVERIFIABLE
    is_valid = Column(Boolean, nullable=False)
    total_errors = Column(Integer, default=0)
    total_missing = Column(Integer, default=0)
    validated_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    spec = relationship("CableSpec", back_populates="validation_results")
    errors = relationship("ValidationError", back_populates="validation_result")


class ValidationError(Base):
    """Individual validation errors/warnings.
    Source: CableValidator violations[] and missing_data[]
    """
    __tablename__ = "validation_errors"

    error_id = Column(Integer, primary_key=True)
    validation_id = Column(Integer, ForeignKey("validation_results.validation_id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("validation_rules.rule_id"))
    error_type = Column(String(20), nullable=False)  # violation / missing_data
    message = Column(Text, nullable=False)
    field_name = Column(String(50))  # Which spec field this relates to
    severity = Column(String(20), default="error")  # error / warning

    # Relationships
    validation_result = relationship("ValidationResult", back_populates="errors")
    rule = relationship("ValidationRule", back_populates="error_records")


class ValidationHistory(Base):
    """Human review / override records for validation results."""
    __tablename__ = "validation_history"

    validation_history_id = Column(Integer, primary_key=True)
    spec_id = Column(Integer, ForeignKey("cable_specs.spec_id"), nullable=False)
    validation_id = Column(Integer, ForeignKey("validation_results.validation_id"))
    reviewer_id = Column(Integer, ForeignKey("users.user_id"))
    corrected_data = Column(JSON)  # Changed from Text to JSON for structured data
    was_ai_correct = Column(Boolean)
    reviewer_notes = Column(Text)
    review_date = Column(TIMESTAMP, server_default="now()")

    # Relationships
    spec = relationship("CableSpec", back_populates="validation_history")
    reviewer = relationship("User", back_populates="validation_reviews")
    validation_result = relationship("ValidationResult")


# ═══════════════════════════════════════════════════════════════════
# 8. KEYWORD GENERATION & CABLE CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════

class KeywordPattern(Base):
    """Regex patterns for keyword extraction.
    Source: Keyword_Generator/keyword_tool.py — KeywordExtractor.patterns
    """
    __tablename__ = "keyword_patterns"

    pattern_id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False)  # Voltage, Current, CrossSection, etc.
    regex_pattern = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default="now()")


class CableCategory(Base):
    """Cable classification categories.
    Source: Keyword_Generator/keyword_tool.py — CableClassifier.categories
    """
    __tablename__ = "cable_categories"

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(80), nullable=False, unique=True)
    voltage_min_v = Column(Float)  # Voltage range lower bound
    voltage_max_v = Column(Float)  # Voltage range upper bound
    priority = Column(Integer, default=0)  # Classification priority (higher = more specific)
    description = Column(Text)

    # Relationships
    category_keywords = relationship("CategoryKeyword", back_populates="category")
    classification_results = relationship("ClassificationResult", back_populates="category")


class CategoryKeyword(Base):
    """Keywords used for cable category matching.
    Source: Keyword_Generator/keyword_tool.py — CableClassifier.categories keyword lists
    """
    __tablename__ = "category_keywords"

    keyword_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("cable_categories.category_id"), nullable=False)
    keyword = Column(String(100), nullable=False)
    match_type = Column(String(20), default="text")  # text / voltage_threshold

    __table_args__ = (
        UniqueConstraint("category_id", "keyword", name="uq_cat_keyword"),
    )

    # Relationships
    category = relationship("CableCategory", back_populates="category_keywords")


class ClassificationResult(Base):
    """Classification result linking a spec to a category."""
    __tablename__ = "classification_results"

    classification_id = Column(Integer, primary_key=True)
    spec_id = Column(Integer, ForeignKey("cable_specs.spec_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("cable_categories.category_id"), nullable=False)
    confidence = Column(Float)
    max_voltage_detected = Column(Float)  # Voltage used for threshold classification
    classification_method = Column(String(20))  # keyword / voltage_threshold / hybrid
    classified_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    spec = relationship("CableSpec")
    category = relationship("CableCategory", back_populates="classification_results")


class Keyword(Base):
    """Generated keywords per cable spec.
    Source: Keyword_Generator/keyword_tool.py — KeywordExtractor.extract_keywords()
    """
    __tablename__ = "keywords"

    keyword_id = Column(Integer, primary_key=True)
    spec_id = Column(Integer, ForeignKey("cable_specs.spec_id"), nullable=False)
    keyword_text = Column(String(100), nullable=False)
    category = Column(String(50))  # Voltage, Current, Material, Top Terms, etc.
    weight = Column(Float, default=1.0)  # 0.5 for Top Terms, 1.0 for spec terms
    source = Column(String(20), default="auto")  # auto / manual

    # Relationships
    spec = relationship("CableSpec", back_populates="keywords")


# ═══════════════════════════════════════════════════════════════════
# 9. VISION INSPECTION (YOLO)
# ═══════════════════════════════════════════════════════════════════

class Inspection(Base):
    """Vision inspection session for a document/image."""
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.doc_id"), nullable=False)
    model_version_id = Column(Integer, ForeignKey("model_versions.model_id"))

    image_path = Column(Text)
    processed_image_path = Column(Text)
    image_width_px = Column(Integer)
    image_height_px = Column(Integer)

    status = Column(String(20))  # completed / failed / pending
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    document = relationship("Document", back_populates="inspections")
    model_version = relationship("ModelVersion")
    segmentation_results = relationship("SegmentationResult", back_populates="inspection")
    cnn_results = relationship("CNNResult", back_populates="inspection")
    detection_results = relationship("DetectionResult", back_populates="inspection")
    linked_specs = relationship("CableSpec", back_populates="linked_inspection")


class DetectionClass(Base):
    """YOLO model detection classes.
    Source: Vision_Model/Cable_Dataset/classes.txt.txt
    """
    __tablename__ = "detection_classes"

    class_id = Column(Integer, primary_key=True)
    class_name = Column(String(50), nullable=False, unique=True)  # Conductor, Insulation, Sheath_Jacket, Filler, Armour
    description = Column(Text)
    color_code = Column(String(7))  # Hex color for visualization, e.g. "#FF0000"


class DetectionResult(Base):
    """Individual bounding box detections from YOLO inference.
    Source: Vision_Model/src/analyzer.py — all_detections list
    """
    __tablename__ = "detection_results"

    detection_id = Column(Integer, primary_key=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("detection_classes.class_id"))

    # Bounding box coordinates
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)

    # Measurements
    width_px = Column(Float)
    height_px = Column(Float)
    area_px = Column(Float)
    diameter_mm = Column(Float)

    # Confidence
    confidence = Column(Float)

    # QC
    is_primary = Column(Boolean, default=False)  # Largest detection per image

    # Relationships
    inspection = relationship("Inspection", back_populates="detection_results")
    detection_class = relationship("DetectionClass")


class SegmentationResult(Base):
    """Segmentation / measurement results from vision analysis."""
    __tablename__ = "segmentation_results"

    id = Column(Integer, primary_key=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)

    mask_area = Column(Float)
    width_px = Column(Float)
    diameter_mm = Column(Float)
    confidence = Column(Float)
    detection_method = Column(String(20))  # yolo_box / mask / fallback_box
    contour_points = Column(JSON)  # Changed from Text to JSON for structured data
    qc_status = Column(String(20))  # PASS / FAIL
    qc_reason = Column(String(100))  # e.g. "Too Small"

    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    inspection = relationship("Inspection", back_populates="segmentation_results")


class CNNResult(Base):
    """CNN classification results."""
    __tablename__ = "cnn_results"

    id = Column(Integer, primary_key=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)

    predicted_class = Column(String(50))
    confidence = Column(Float)
    model_version = Column(String(50))
    all_predictions = Column(JSON)  # Top-N class probabilities

    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    inspection = relationship("Inspection", back_populates="cnn_results")


# ═══════════════════════════════════════════════════════════════════
# 10. MODEL CONFIG & VERSIONING
# ═══════════════════════════════════════════════════════════════════

class ModelVersion(Base):
    """AI model version tracking (OCR + Vision models)."""
    __tablename__ = "model_versions"

    model_id = Column(Integer, primary_key=True)
    model_type = Column(String(20), nullable=False)  # yolo / ocr / spacy
    model_name = Column(String(100), nullable=False)  # e.g. yolov8m-seg
    version_tag = Column(String(20), nullable=False)  # e.g. v1.0, v2.1
    file_path = Column(Text)  # Path to model weights
    framework = Column(String(30))  # ultralytics / easyocr / spacy
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    trained_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    training_session = relationship("TrainingSession", back_populates="model_version", uselist=False)


class VisionConfigParam(Base):
    """Configurable vision module parameters.
    Source: Vision_Model/config/settings.py
    """
    __tablename__ = "vision_config_params"

    param_id = Column(Integer, primary_key=True)
    param_key = Column(String(50), nullable=False, unique=True)
    param_value = Column(Text, nullable=False)
    value_type = Column(String(20), default="float")  # float / int / string / bool
    description = Column(Text)
    updated_at = Column(TIMESTAMP, server_default="now()")


class DiameterSpecRule(Base):
    """Diameter-to-specification estimation rules.
    Source: Vision_Model/config/settings.py — get_cable_specs()
    """
    __tablename__ = "diameter_spec_rules"

    rule_id = Column(Integer, primary_key=True)
    min_diameter_mm = Column(Float, nullable=False)
    max_diameter_mm = Column(Float, nullable=False)  # Upper bound (exclusive)
    voltage_class = Column(String(50))
    conductor_class = Column(String(50))
    insulation_type = Column(String(50))
    sheath_material = Column(String(50))
    cable_type = Column(String(50))
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("min_diameter_mm < max_diameter_mm", name="ck_diameter_range"),
    )


# ═══════════════════════════════════════════════════════════════════
# 11. TRAINING TRACKING
# ═══════════════════════════════════════════════════════════════════

class TrainingSession(Base):
    """YOLO/OCR model training session tracking.
    Source: Vision_Model/src/trainer.py
    """
    __tablename__ = "training_sessions"

    session_id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("model_versions.model_id"))
    model_size = Column(String(30))  # yolov8m-seg.pt, etc.
    epochs = Column(Integer)
    batch_size = Column(Integer)
    img_size = Column(Integer)
    device = Column(String(10))  # cuda / cpu
    data_yaml_path = Column(Text)
    status = Column(String(20), default="pending")  # pending / running / completed / failed
    best_model_path = Column(Text)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default="now()")

    # Relationships
    model_version = relationship("ModelVersion", back_populates="training_session")
    metrics = relationship("TrainingMetric", back_populates="session")


class TrainingMetric(Base):
    """Per-epoch training metrics."""
    __tablename__ = "training_metrics"

    metric_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("training_sessions.session_id"), nullable=False)
    epoch = Column(Integer, nullable=False)
    train_loss = Column(Float)
    val_loss = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    mAP50 = Column(Float)
    mAP50_95 = Column(Float)
    learning_rate = Column(Float)
    epoch_duration_sec = Column(Float)

    # Relationships
    session = relationship("TrainingSession", back_populates="metrics")
