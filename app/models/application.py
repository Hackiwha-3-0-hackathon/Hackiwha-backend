from sqlalchemy import String, DateTime, Float, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
import enum
from app.db.base_class import Base


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"

class VerificationStatus(str, enum.Enum):
    not_submitted = "not_submitted"   
    pending = "pending"                
    verified = "verified"              
    flagged = "flagged"                


class Application(Base):

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    social_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.pending, nullable=False
    )

    applied_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )

   
    submitted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), default=VerificationStatus.not_submitted, nullable=False
    )
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    current_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    engagement_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    amount_paid: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    campaign: Mapped["Campaign"] = relationship(back_populates="applications")
    
    user: Mapped["User"] = relationship(back_populates="applications")
