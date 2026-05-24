# db/crud.py
"""Database CRUD operations for SpecSense AI — Full Schema."""

from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import (
    # User & Documents
    User, Document,
    # OCR Pipeline
    OCRSession, OCRPageResult,
    # Extraction
    ExtractionPattern, PreprocessingRule,
    # Correction
    CorrectionRule, ExtractionRun, CorrectionLog,
    # Cable Specifications
    CableType, Standard, CableSpec, SpecFieldValue,
    # Validation
    ValidationRule, ValidationRuleParameter, MaterialWhitelist,
    IECStandardSize, ValidationResult, ValidationError, ValidationHistory,
    # Keywords & Classification
    KeywordPattern, CableCategory, CategoryKeyword,
    ClassificationResult, Keyword,
    # Vision Inspection
    Inspection, DetectionClass, DetectionResult,
    SegmentationResult, CNNResult,
    # Model Config & Versioning
    ModelVersion, VisionConfigParam, DiameterSpecRule,
    # Training
    TrainingSession, TrainingMetric,
)


# ═══════════════════════════════════════════════════════════════════
# SESSION HELPER
# ═══════════════════════════════════════════════════════════════════

def get_db():
    """Generator that yields a database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════
# 1. USER CRUD
# ═══════════════════════════════════════════════════════════════════

def create_user(db: Session, full_name: str, email: str, role: str = "viewer"):
    user = User(full_name=full_name, email=email, role=role, created_at=datetime.now())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# ═══════════════════════════════════════════════════════════════════
# 2. DOCUMENT CRUD
# ═══════════════════════════════════════════════════════════════════

def create_document(
    db: Session, file_name: str, file_path: str, file_type: str,
    file_size_kb: float = None, file_hash: str = None,
    page_count: int = None, uploaded_by: int = None, status: str = "uploaded"
):
    doc = Document(
        file_name=file_name, file_path=file_path, file_type=file_type,
        file_size_kb=file_size_kb, file_hash=file_hash,
        page_count=page_count, uploaded_by=uploaded_by,
        upload_date=datetime.now(), status=status
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document_by_id(db: Session, doc_id: int):
    return db.query(Document).filter(Document.doc_id == doc_id).first()


def get_documents_by_status(db: Session, status: str):
    return db.query(Document).filter(Document.status == status).all()


# ═══════════════════════════════════════════════════════════════════
# 3. OCR SESSION CRUD
# ═══════════════════════════════════════════════════════════════════

def create_ocr_session(
    db: Session, doc_id: int, languages: str = "en",
    gpu_enabled: bool = True, total_pages: int = None, status: str = "running"
):
    session = OCRSession(
        doc_id=doc_id, languages=languages, gpu_enabled=gpu_enabled,
        total_pages=total_pages, status=status, created_at=datetime.now()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_ocr_session(
    db: Session, session_id: int, total_chars: int = None,
    processing_time_ms: int = None, status: str = None
):
    session = db.query(OCRSession).filter(OCRSession.session_id == session_id).first()
    if not session:
        return None
    if total_chars is not None:
        session.total_chars = total_chars
    if processing_time_ms is not None:
        session.processing_time_ms = processing_time_ms
    if status is not None:
        session.status = status
    db.commit()
    db.refresh(session)
    return session


def create_ocr_page_result(
    db: Session, session_id: int, page_number: int,
    raw_text: str, confidence_avg: float = None, word_count: int = None
):
    result = OCRPageResult(
        session_id=session_id, page_number=page_number,
        raw_text=raw_text, confidence_avg=confidence_avg,
        word_count=word_count, created_at=datetime.now()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


# ═══════════════════════════════════════════════════════════════════
# 4. EXTRACTION PATTERN CRUD
# ═══════════════════════════════════════════════════════════════════

def create_extraction_pattern(
    db: Session, field_name: str, regex_pattern: str,
    language: str = "en", description: str = None,
    priority: int = 0, is_active: bool = True
):
    pattern = ExtractionPattern(
        field_name=field_name, language=language,
        regex_pattern=regex_pattern, description=description,
        priority=priority, is_active=is_active
    )
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern


def get_active_extraction_patterns(db: Session, language: str = "en"):
    return (
        db.query(ExtractionPattern)
        .filter(ExtractionPattern.is_active == True, ExtractionPattern.language == language)
        .order_by(ExtractionPattern.priority.desc())
        .all()
)


def create_preprocessing_rule(
    db: Session, rule_type: str, search_regex: str, replacement: str,
    flags: str = "IGNORECASE", description: str = None,
    execution_order: int = 0, is_active: bool = True
):
    rule = PreprocessingRule(
        rule_type=rule_type, search_regex=search_regex,
        replacement=replacement, flags=flags,
        description=description, execution_order=execution_order,
        is_active=is_active
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_active_preprocessing_rules(db: Session):
    return (
        db.query(PreprocessingRule)
        .filter(PreprocessingRule.is_active == True)
        .order_by(PreprocessingRule.execution_order)
        .all()
)

# 5. CORRECTION CRUD

def create_correction_rule(
    db: Session, field_name: str, rule_type: str,
    abbreviation: str = None, expanded_value: str = None,
    search_regex: str = None, replacement: str = None,
    description: str = None, is_active: bool = True
):
    rule = CorrectionRule(
        field_name=field_name, rule_type=rule_type,
        abbreviation=abbreviation, expanded_value=expanded_value,
        search_regex=search_regex, replacement=replacement,
        description=description, is_active=is_active
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_correction_rules_by_field(db: Session, field_name: str):
    return (
        db.query(CorrectionRule)
        .filter(CorrectionRule.field_name == field_name, CorrectionRule.is_active == True)
        .all()
)


def create_extraction_run(
    db: Session, session_id: int, raw_specs_json: dict = None,
    corrected_specs_json: dict = None, extraction_method: str = "regex",
    total_fields_extracted: int = None, total_corrections_applied: int = None
):
    run = ExtractionRun(
        session_id=session_id, raw_specs_json=raw_specs_json,
        corrected_specs_json=corrected_specs_json,
        extraction_method=extraction_method,
        total_fields_extracted=total_fields_extracted,
        total_corrections_applied=total_corrections_applied,
        created_at=datetime.now()
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def create_correction_log(
    db: Session, run_id: int, field_name: str,
    original_value: str, corrected_value: str, reason: str
):
    log = CorrectionLog(
        run_id=run_id, field_name=field_name,
        original_value=original_value, corrected_value=corrected_value,
        reason=reason, created_at=datetime.now()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def create_correction_logs_batch(db: Session, run_id: int, logs: list):
    """Batch create correction logs from SpecCorrector.corrections_log.
    Args:
        logs: list of strings like "Voltage: Changed '0.6/1kV' to '0.6/1 kV' (Formatting)"
    """
    created = []
    for log_str in logs:
        # Parse "Field: Changed 'old' to 'new' (Reason)"
        parts = log_str.split(": Changed ", 1)
        field_name = parts[0].strip() if len(parts) > 1 else "unknown"
        rest = parts[1] if len(parts) > 1 else log_str
        # Extract old/new/reason
        original = ""
        corrected = ""
        reason = ""
        if "' to '" in rest:
            original_part, rest_part = rest.split("' to '", 1)
            original = original_part.strip("' ")
            if "'" in rest_part:
                corrected = rest_part.split("'")[0]
                reason_part = rest_part.split("(")
                if len(reason_part) > 1:
                    reason = reason_part[-1].rstrip(")")

        log = CorrectionLog(
            run_id=run_id, field_name=field_name,
            original_value=original, corrected_value=corrected_value,
            reason=reason, created_at=datetime.now()
        )
        db.add(log)
        created.append(log)

    db.commit()
    for log in created:
        db.refresh(log)
    return created



# 6. CABLE SPECIFICATION CRUD


def create_cable_type(db: Session, type_name: str, description: str = None):
    ct = CableType(type_name=type_name, description=description)
    db.add(ct)
    db.commit()
    db.refresh(ct)
    return ct


def create_standard(db: Session, standard_name: str, description: str = None, version: str = None):
    std = Standard(standard_name=standard_name, description=description, version=version)
    db.add(std)
    db.commit()
    db.refresh(std)
    return std


def create_cable_spec(
    db: Session, doc_id: int,
    cable_type_id: int = None, standard_id: int = None, run_id: int = None,
    voltage_rating: str = None, current_rating: str = None,
    conductor_material: str = None, conductor_class: str = None,
    insulation_type: str = None, number_of_cores: int = None,
    cross_section_area: str = None, armor_type: str = None,
    sheath_material: str = None, fire_performance: str = None,
    operating_temperature: str = None, insulation_resistance: str = None,
    is_verified: bool = False, extraction_confidence: float = None,
    extraction_method: str = "regex", linked_inspection_id: int = None
):
    spec = CableSpec(
        doc_id=doc_id, cable_type_id=cable_type_id,
        standard_id=standard_id, run_id=run_id,
        voltage_rating=voltage_rating, current_rating=current_rating,
        conductor_material=conductor_material, conductor_class=conductor_class,
        insulation_type=insulation_type, number_of_cores=number_of_cores,
        cross_section_area=cross_section_area, armor_type=armor_type,
        sheath_material=sheath_material, fire_performance=fire_performance,
        operating_temperature=operating_temperature,
        insulation_resistance=insulation_resistance,
        is_verified=is_verified, extraction_confidence=extraction_confidence,
        extraction_method=extraction_method,
        linked_inspection_id=linked_inspection_id,
        created_at=datetime.now()
    )
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec


def get_cable_spec_by_doc(db: Session, doc_id: int):
    return db.query(CableSpec).filter(CableSpec.doc_id == doc_id).first()


def create_spec_field_value(
    db: Session, spec_id: int, field_name: str,
    raw_value: str = None, corrected_value: str = None,
    confidence: float = None, source: str = "regex",
    matched_pattern_id: int = None, page_number: int = None
):
    val = SpecFieldValue(
        spec_id=spec_id, field_name=field_name,
        raw_value=raw_value, corrected_value=corrected_value,
        confidence=confidence, source=source,
        matched_pattern_id=matched_pattern_id,
        page_number=page_number, created_at=datetime.now()
    )
    db.add(val)
    db.commit()
    db.refresh(val)
    return val



# 7. VALIDATION CRUD

def create_validation_rule(
    db: Session, rule_code: str, rule_name: str,
    description: str = None, severity: str = "error", is_active: bool = True
):
    rule = ValidationRule(
        rule_code=rule_code, rule_name=rule_name,
        description=description, severity=severity, is_active=is_active
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_active_validation_rules(db: Session):
    return db.query(ValidationRule).filter(ValidationRule.is_active == True).all()


def create_validation_rule_parameter(
    db: Session, rule_id: int, param_key: str, param_value: str,
    value_type: str = "string", description: str = None
):
    param = ValidationRuleParameter(
        rule_id=rule_id, param_key=param_key,
        param_value=param_value, value_type=value_type,
        description=description
    )
    db.add(param)
    db.commit()
    db.refresh(param)
    return param


def create_material_whitelist(
    db: Session, category: str, material_name: str,
    description: str = None, is_active: bool = True
):
    mat = MaterialWhitelist(
        category=category, material_name=material_name,
        description=description, is_active=is_active
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)
    return mat


def get_materials_by_category(db: Session, category: str):
    return (
        db.query(MaterialWhitelist)
        .filter(MaterialWhitelist.category == category, MaterialWhitelist.is_active == True)
        .all()
)


def create_iec_standard_size(
    db: Session, size_mm2: float, tolerance_pct: float = 5.0,
    standard_id: int = None, description: str = None
):
    size = IECStandardSize(
        size_mm2=size_mm2, tolerance_pct=tolerance_pct,
        standard_id=standard_id, description=description
    )
    db.add(size)
    db.commit()
    db.refresh(size)
    return size


def get_all_iec_standard_sizes(db: Session):
    return db.query(IECStandardSize).all()


def create_validation_result(
    db: Session, spec_id: int, status: str, is_valid: bool,
    total_errors: int = 0, total_missing: int = 0
):
    result = ValidationResult(
        spec_id=spec_id, status=status, is_valid=is_valid,
        total_errors=total_errors, total_missing=total_missing,
        validated_at=datetime.now()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def create_validation_error(
    db: Session, validation_id: int, error_type: str, message: str,
    rule_id: int = None, field_name: str = None, severity: str = "error"
):
    error = ValidationError(
        validation_id=validation_id, rule_id=rule_id,
        error_type=error_type, message=message,
        field_name=field_name, severity=severity
    )
    db.add(error)
    db.commit()
    db.refresh(error)
    return error


def create_validation_errors_batch(db: Session, validation_id: int, errors: list, error_type: str = "violation"):
    """Batch create validation errors from CableValidator output."""
    created = []
    for err_msg in errors:
        error = ValidationError(
            validation_id=validation_id, error_type=error_type,
            message=err_msg, severity="error" if error_type == "violation" else "warning"
        )
        db.add(error)
        created.append(error)
    db.commit()
    for e in created:
        db.refresh(e)
    return created


def create_validation_history(
    db: Session, spec_id: int, reviewer_id: int = None,
    validation_id: int = None, corrected_data: dict = None,
    was_ai_correct: bool = None, reviewer_notes: str = None
):
    history = ValidationHistory(
        spec_id=spec_id, reviewer_id=reviewer_id,
        validation_id=validation_id, corrected_data=corrected_data,
        was_ai_correct=was_ai_correct, reviewer_notes=reviewer_notes,
        review_date=datetime.now()
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


# ═══════════════════════════════════════════════════════════════════
# 8. KEYWORD & CLASSIFICATION CRUD
# ═══════════════════════════════════════════════════════════════════

def create_keyword_pattern(
    db: Session, label: str, regex_pattern: str,
    description: str = None, is_active: bool = True
):
    pattern = KeywordPattern(
        label=label, regex_pattern=regex_pattern,
        description=description, is_active=is_active
    )
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern


def get_active_keyword_patterns(db: Session):
    return db.query(KeywordPattern).filter(KeywordPattern.is_active == True).all()


def create_cable_category(
    db: Session, category_name: str,
    voltage_min_v: float = None, voltage_max_v: float = None,
    priority: int = 0, description: str = None
):
    cat = CableCategory(
        category_name=category_name,
        voltage_min_v=voltage_min_v, voltage_max_v=voltage_max_v,
        priority=priority, description=description
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def create_category_keyword(
    db: Session, category_id: int, keyword: str, match_type: str = "text"
):
    kw = CategoryKeyword(category_id=category_id, keyword=keyword, match_type=match_type)
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


def create_classification_result(
    db: Session, spec_id: int, category_id: int,
    confidence: float = None, max_voltage_detected: float = None,
    classification_method: str = "hybrid"
):
    result = ClassificationResult(
        spec_id=spec_id, category_id=category_id,
        confidence=confidence, max_voltage_detected=max_voltage_detected,
        classification_method=classification_method, classified_at=datetime.now()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def create_keywords(db: Session, spec_id: int, keywords_dict: dict):
    """Create Keyword records from a keyword dictionary.
    Returns the list of created Keyword records.
    """
    created = []
    for category, values in keywords_dict.items():
        weight = 0.5 if category == "Top Terms" else 1.0

        if isinstance(values, list):
            for val in values:
                kw = Keyword(
                    spec_id=spec_id,
                    keyword_text=f"{category}: {val}",
                    category=category,
                    weight=weight
                )
                db.add(kw)
                created.append(kw)
        elif values:
            kw = Keyword(
                spec_id=spec_id,
                keyword_text=f"{category}: {values}",
                category=category,
                weight=weight
            )
            db.add(kw)
            created.append(kw)

    db.commit()
    for kw in created:
        db.refresh(kw)
    return created


# ═══════════════════════════════════════════════════════════════════
# 9. VISION INSPECTION CRUD
# ═══════════════════════════════════════════════════════════════════

def create_inspection(
    db: Session, document_id: int, image_path: str,
    processed_image_path: str = None, model_version_id: int = None,
    image_width_px: int = None, image_height_px: int = None,
    status: str = "completed"
):
    inspection = Inspection(
        document_id=document_id, image_path=image_path,
        processed_image_path=processed_image_path,
        model_version_id=model_version_id,
        image_width_px=image_width_px, image_height_px=image_height_px,
        status=status, created_at=datetime.now()
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection


def create_detection_class(
    db: Session, class_name: str, description: str = None, color_code: str = None
):
    dc = DetectionClass(class_name=class_name, description=description, color_code=color_code)
    db.add(dc)
    db.commit()
    db.refresh(dc)
    return dc


def create_detection_result(
    db: Session, inspection_id: int, class_id: int = None,
    x1: int = None, y1: int = None, x2: int = None, y2: int = None,
    width_px: float = None, height_px: float = None, area_px: float = None,
    diameter_mm: float = None, confidence: float = None, is_primary: bool = False
):
    det = DetectionResult(
        inspection_id=inspection_id, class_id=class_id,
        x1=x1, y1=y1, x2=x2, y2=y2,
        width_px=width_px, height_px=height_px, area_px=area_px,
        diameter_mm=diameter_mm, confidence=confidence, is_primary=is_primary
    )
    db.add(det)
    db.commit()
    db.refresh(det)
    return det


def create_segmentation_result(
    db: Session, inspection_id: int,
    diameter_mm: float = None, width_px: float = None,
    mask_area: float = None, confidence: float = None,
    detection_method: str = "yolo_box", contour_points: dict = None,
    qc_status: str = None, qc_reason: str = None
):
    result = SegmentationResult(
        inspection_id=inspection_id,
        diameter_mm=diameter_mm, width_px=width_px,
        mask_area=mask_area, confidence=confidence,
        detection_method=detection_method, contour_points=contour_points,
        qc_status=qc_status, qc_reason=qc_reason,
        created_at=datetime.now()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def create_cnn_result(
    db: Session, inspection_id: int, predicted_class: str,
    confidence: float, model_version: str = "v1.0",
    all_predictions: dict = None
):
    result = CNNResult(
        inspection_id=inspection_id, predicted_class=predicted_class,
        confidence=confidence, model_version=model_version,
        all_predictions=all_predictions, created_at=datetime.now()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


# ═══════════════════════════════════════════════════════════════════
# 10. MODEL CONFIG & VERSIONING CRUD
# ═══════════════════════════════════════════════════════════════════

def create_model_version(
    db: Session, model_type: str, model_name: str, version_tag: str,
    file_path: str = None, framework: str = None,
    description: str = None, is_active: bool = True
):
    mv = ModelVersion(
        model_type=model_type, model_name=model_name,
        version_tag=version_tag, file_path=file_path,
        framework=framework, description=description,
        is_active=is_active, created_at=datetime.now()
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv


def get_active_model_version(db: Session, model_type: str):
    return (
        db.query(ModelVersion)
        .filter(ModelVersion.model_type == model_type, ModelVersion.is_active == True)
        .first()
    )


def create_vision_config_param(
    db: Session, param_key: str, param_value: str,
    value_type: str = "float", description: str = None
):
    param = VisionConfigParam(
        param_key=param_key, param_value=param_value,
        value_type=value_type, description=description
    )
    db.add(param)
    db.commit()
    db.refresh(param)
    return param


def get_vision_config(db: Session):
    """Return all vision config params as a dict."""
    params = db.query(VisionConfigParam).all()
    return {p.param_key: p.param_value for p in params}


def create_diameter_spec_rule(
    db: Session, min_diameter_mm: float, max_diameter_mm: float,
    voltage_class: str, conductor_class: str, insulation_type: str,
    sheath_material: str, cable_type: str, priority: int = 0
):
    rule = DiameterSpecRule(
        min_diameter_mm=min_diameter_mm, max_diameter_mm=max_diameter_mm,
        voltage_class=voltage_class, conductor_class=conductor_class,
        insulation_type=insulation_type, sheath_material=sheath_material,
        cable_type=cable_type, priority=priority
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_active_diameter_spec_rules(db: Session):
    return (
        db.query(DiameterSpecRule)
        .filter(DiameterSpecRule.is_active == True)
        .order_by(DiameterSpecRule.priority.desc())
        .all()
)


# ═══════════════════════════════════════════════════════════════════
# 11. TRAINING CRUD
# ═══════════════════════════════════════════════════════════════════

def create_training_session(
    db: Session, model_id: int = None, model_size: str = None,
    epochs: int = None, batch_size: int = None, img_size: int = None,
    device: str = None, data_yaml_path: str = None, status: str = "pending"
):
    session = TrainingSession(
        model_id=model_id, model_size=model_size,
        epochs=epochs, batch_size=batch_size, img_size=img_size,
        device=device, data_yaml_path=data_yaml_path,
        status=status, created_at=datetime.now()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_training_session(
    db: Session, session_id: int, status: str = None,
    best_model_path: str = None, completed_at: datetime = None
):
    session = db.query(TrainingSession).filter(TrainingSession.session_id == session_id).first()
    if not session:
        return None
    if status is not None:
        session.status = status
    if best_model_path is not None:
        session.best_model_path = best_model_path
    if completed_at is not None:
        session.completed_at = completed_at
    db.commit()
    db.refresh(session)
    return session


def create_training_metric(
    db: Session, session_id: int, epoch: int,
    train_loss: float = None, val_loss: float = None,
    precision: float = None, recall: float = None,
    mAP50: float = None, mAP50_95: float = None,
    learning_rate: float = None, epoch_duration_sec: float = None
):
    metric = TrainingMetric(
        session_id=session_id, epoch=epoch,
        train_loss=train_loss, val_loss=val_loss,
        precision=precision, recall=recall,
        mAP50=mAP50, mAP50_95=mAP50_95,
        learning_rate=learning_rate, epoch_duration_sec=epoch_duration_sec
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


# ═══════════════════════════════════════════════════════════════════
# CONVENIENCE: Full Pipeline Save (OCR Path)
# ═══════════════════════════════════════════════════════════════════

def save_ocr_pipeline_results(
    db: Session,
    file_name: str, file_path: str, file_type: str,
    full_text: str, raw_specs: dict, clean_specs: dict,
    correction_logs: list, validation_result: dict,
    keywords_dict: dict, category_name: str,
    extraction_method: str = "regex"
):
    """Convenience function to save the complete OCR pipeline results.
    Creates: Document → OCRSession → ExtractionRun → CableSpec →
             ValidationResult + Errors + Keywords + Classification
    """
    # 1. Document
    doc = create_document(db, file_name=file_name, file_path=file_path, file_type=file_type)

    # 2. OCR Session
    ocr_session = create_ocr_session(db, doc_id=doc.doc_id, status="completed")

    # 3. Page result (single page for simplicity)
    create_ocr_page_result(
        db, session_id=ocr_session.session_id, page_number=1,
        raw_text=full_text, word_count=len(full_text.split())
    )

    # 4. Extraction Run
    run = create_extraction_run(
        db, session_id=ocr_session.session_id,
        raw_specs_json=raw_specs, corrected_specs_json=clean_specs,
        extraction_method=extraction_method,
        total_fields_extracted=sum(1 for v in raw_specs.values() if v),
        total_corrections_applied=len(correction_logs)
    )

    # 5. Correction Logs
    if correction_logs:
        create_correction_logs_batch(db, run_id=run.run_id, logs=correction_logs)

    # 6. Cable Spec
    spec = create_cable_spec(
        db, doc_id=doc.doc_id, run_id=run.run_id,
        voltage_rating=clean_specs.get('voltage'),
        current_rating=clean_specs.get('current_rating'),
        conductor_material=clean_specs.get('cable_type'),
        insulation_type=clean_specs.get('insulation'),
        number_of_cores=clean_specs.get('conductor_count'),
        cross_section_area=clean_specs.get('conductor_size'),
        armor_type=clean_specs.get('armor'),
        sheath_material=clean_specs.get('sheath'),
        operating_temperature=clean_specs.get('operating_temperature'),
        insulation_resistance=clean_specs.get('insulation_resistance'),
        is_verified=validation_result.get('valid', False),
        extraction_confidence=1.0,
        extraction_method=extraction_method
    )

    # 7. Validation Result
    val_result = create_validation_result(
        db, spec_id=spec.spec_id,
        status=validation_result.get('status', 'UNKNOWN'),
        is_valid=validation_result.get('valid', False),
        total_errors=len(validation_result.get('errors', [])),
        total_missing=len(validation_result.get('missing', []))
    )

    # 8. Validation Errors
    if validation_result.get('errors'):
        create_validation_errors_batch(
            db, validation_id=val_result.validation_id,
            errors=validation_result['errors'], error_type="violation"
        )
    if validation_result.get('missing'):
        create_validation_errors_batch(
            db, validation_id=val_result.validation_id,
            errors=validation_result['missing'], error_type="missing_data"
        )

    # 9. Keywords
    if keywords_dict:
        create_keywords(db, spec_id=spec.spec_id, keywords_dict=keywords_dict)

    # 10. Classification
    if category_name:
        cat = db.query(CableCategory).filter(CableCategory.category_name == category_name).first()
        if cat:
            create_classification_result(
                db, spec_id=spec.spec_id, category_id=cat.category_id,
                classification_method="keyword"
            )

    return {
        "document": doc,
        "ocr_session": ocr_session,
        "extraction_run": run,
        "spec": spec,
        "validation_result": val_result
    }


# ═══════════════════════════════════════════════════════════════════
# CONVENIENCE: Full Pipeline Save (Vision Path)
# ═══════════════════════════════════════════════════════════════════

def save_vision_pipeline_results(
    db: Session,
    file_name: str, file_path: str, file_type: str,
    cable_data_list: list, model_version_id: int = None
):
    """Convenience function to save the complete Vision pipeline results.
    Creates: Document → Inspection → DetectionResults + SegmentationResult
    """
    # 1. Document
    doc = create_document(db, file_name=file_name, file_path=file_path, file_type=file_type)

    # 2. Inspection
    inspection = create_inspection(
        db, document_id=doc.doc_id, image_path=file_path,
        model_version_id=model_version_id,
        status="completed"
    )

    # 3. Detection & Segmentation results
    for cable_data in cable_data_list:
        if "Error" in cable_data:
            continue

        # Segmentation result
        create_segmentation_result(
            db, inspection_id=inspection.id,
            diameter_mm=cable_data.get("Diameter (mm)"),
            detection_method="yolo_box",
            qc_status="PASS" if "PASS" in cable_data.get("Status", "") else "FAIL",
            qc_reason=cable_data.get("Status", "")
        )

    return {
        "document": doc,
        "inspection": inspection
    }
