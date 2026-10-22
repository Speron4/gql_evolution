from typing import Optional
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.DBDefinitions.BaseModel import BaseDBModel, UUIDFKey, IDType

class NotificationRuleModel(BaseDBModel):
    __tablename__ = "notification_rules"

    id: Mapped[IDType] = mapped_column(primary_key=True, default=None, nullable=True)
    
    owner_id: Mapped[Optional[IDType]] = mapped_column(index=True, default=None, nullable=True, comment="Owner of the rule")
    entity_id: Mapped[Optional[IDType]] = mapped_column(index=True, default=None, nullable=True, comment="Identifier of the tracked entity")
    
    entity_type_id: Mapped[Optional[IDType]] = UUIDFKey(ForeignKey("notification_types.id"), default=None, nullable=True, comment="Type of the tracked entity")
    activity_type_id: Mapped[Optional[IDType]] = UUIDFKey(ForeignKey("notification_types.id"), default=None, nullable=True, comment="Type of the activity to react to")
    enabled: Mapped[Optional[bool]] = mapped_column(Boolean, default=True, nullable=True, comment="Whether the rule is active")