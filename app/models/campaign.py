import datetime
import enum
from sqlalchemy import String, Text, Float, Integer, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class CampaignStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    closed = "closed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)

    reward: Mapped[float] = mapped_column(Float, nullable=False)

    target_views: Mapped[int] = mapped_column(Integer, nullable=False)

    total_budget: Mapped[float | None] = mapped_column(Float, nullable=True)

    deadline: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)

    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus), default=CampaignStatus.draft, nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )

    brand: Mapped["Brand"] = relationship(back_populates="campaigns")
    
    applications: Mapped[list["Application"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
