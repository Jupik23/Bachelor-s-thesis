from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.models.drug_interaction import DrugInteraction
from app.schemas.drug_interaction import DrugInteractionCreate

def create_new_drug_interaction(db: Session, interaction_data: DrugInteractionCreate):
    new_interaction = DrugInteraction(
        drug1 = interaction_data.drug1.lower(),
        drug2 = interaction_data.drug2.lower(),
        description = interaction_data.description,
        severity = interaction_data.severity
    )
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    return new_interaction

def get_interaction(db: Session, drug1: str, drug2: str):
    drug1 = drug1.lower()
    drug2 = drug2.lower()
    db_interaction = db.query(DrugInteraction).filter(
        or_(
            and_(DrugInteraction.drug1 == drug1, DrugInteraction.drug2 == drug2),
            and_(DrugInteraction.drug1 == drug2, DrugInteraction.drug2 == drug1) 
            )
    ).first()
    return db_interaction