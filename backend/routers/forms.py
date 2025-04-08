from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from core.auth import get_current_user
from core.rate_limit import api_limiter

router = APIRouter()

class SelectOption(BaseModel):
    value: str
    label: str

class FormValidationResponse(BaseModel):
    isValid: bool
    errors: dict

@router.get("/select-options/{form_type}", response_model=List[SelectOption])
async def get_select_options(
    form_type: str,
    current_user = Depends(get_current_user)
):
    """
    Get options for select components based on form type.
    """
    options_map = {
        "job_types": [
            {"value": "full_time", "label": "Full Time"},
            {"value": "part_time", "label": "Part Time"},
            {"value": "contract", "label": "Contract"},
            {"value": "internship", "label": "Internship"}
        ],
        "experience_levels": [
            {"value": "entry", "label": "Entry Level"},
            {"value": "mid", "label": "Mid Level"},
            {"value": "senior", "label": "Senior Level"},
            {"value": "lead", "label": "Lead"},
            {"value": "executive", "label": "Executive"}
        ],
        "locations": [
            {"value": "remote", "label": "Remote"},
            {"value": "onsite", "label": "On-site"},
            {"value": "hybrid", "label": "Hybrid"}
        ]
    }
    
    if form_type not in options_map:
        raise HTTPException(status_code=404, detail=f"Form type {form_type} not found")
    
    return options_map[form_type]

@router.post("/validate/{form_type}", response_model=FormValidationResponse)
async def validate_form(
    form_type: str,
    form_data: dict,
    current_user = Depends(get_current_user)
):
    """
    Validate form data based on form type.
    """
    validation_rules = {
        "job_post": {
            "title": {"required": True, "min_length": 5, "max_length": 100},
            "description": {"required": True, "min_length": 50},
            "job_type": {"required": True, "allowed_values": ["full_time", "part_time", "contract", "internship"]},
            "location": {"required": True, "allowed_values": ["remote", "onsite", "hybrid"]},
            "experience_level": {"required": True, "allowed_values": ["entry", "mid", "senior", "lead", "executive"]}
        },
        "candidate_profile": {
            "full_name": {"required": True, "min_length": 2, "max_length": 100},
            "email": {"required": True, "email": True},
            "phone": {"required": True, "pattern": r"^\+?1?\d{9,15}$"},
            "experience_years": {"required": True, "min": 0, "max": 50}
        }
    }
    
    if form_type not in validation_rules:
        raise HTTPException(status_code=404, detail=f"Form type {form_type} not found")
    
    errors = {}
    rules = validation_rules[form_type]
    
    for field, rule in rules.items():
        if field not in form_data and rule.get("required", False):
            errors[field] = "This field is required"
            continue
            
        if field in form_data:
            value = form_data[field]
            
            if rule.get("min_length") and len(value) < rule["min_length"]:
                errors[field] = f"Minimum length is {rule['min_length']} characters"
            
            if rule.get("max_length") and len(value) > rule["max_length"]:
                errors[field] = f"Maximum length is {rule['max_length']} characters"
            
            if rule.get("allowed_values") and value not in rule["allowed_values"]:
                errors[field] = f"Invalid value. Allowed values are: {', '.join(rule['allowed_values'])}"
            
            if rule.get("min") is not None and value < rule["min"]:
                errors[field] = f"Minimum value is {rule['min']}"
            
            if rule.get("max") is not None and value > rule["max"]:
                errors[field] = f"Maximum value is {rule['max']}"
            
            if rule.get("email") and not "@" in value:
                errors[field] = "Invalid email format"
            
            if rule.get("pattern"):
                import re
                if not re.match(rule["pattern"], value):
                    errors[field] = "Invalid format"
    
    return FormValidationResponse(
        isValid=len(errors) == 0,
        errors=errors
    ) 