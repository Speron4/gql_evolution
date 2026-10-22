from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.DBDefinitions.BaseModel import BaseDBModel, IDType, UUIDFKey

class NotificationTypeModel(BaseDBModel):
    """
    Číselník pro typy entit a typy aktivit (stromová struktura).
    """
    __tablename__ = "notification_types"

    id: Mapped[IDType] = mapped_column(primary_key=True, default=None, nullable=True)
    
    # Přidáno default=""
    name: Mapped[str] = mapped_column(String, default="", nullable=True, comment="Název typu (např. 'Projekt', 'Změna stavu')")
    
    # Přidáno default=None
    name_en: Mapped[Optional[str]] = mapped_column(String, default=None, nullable=True, comment="Anglický název")
    
    parent_id: Mapped[Optional[IDType]] = mapped_column(ForeignKey("notification_types.id"), default=None, nullable=True, comment="ID nadřazeného typu")

    parent = relationship(
        "NotificationTypeModel",
        remote_side="NotificationTypeModel.id",
        primaryjoin="NotificationTypeModel.id == NotificationTypeModel.parent_id",
        uselist=False,
        viewonly=True,
        default=None
    )