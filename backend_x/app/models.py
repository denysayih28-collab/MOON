import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base, UTCDateTime


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DataSource(str, enum.Enum):
    manual = "manual"
    simulated = "simulated"
    public_dataset = "public_dataset"


class AlertLevel(str, enum.Enum):
    information = "information"
    attention = "attention"
    high_priority = "high_priority"


class AlertStatus(str, enum.Enum):
    active = "active"
    acknowledged = "acknowledged"
    resolved = "resolved"


class Operator(str, enum.Enum):
    gt = ">"
    gte = ">="
    lt = "<"
    lte = "<="


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    start_date: Mapped[datetime] = mapped_column(UTCDateTime)
    planned_days: Mapped[int] = mapped_column(Integer, default=180)

    astronauts: Mapped[list["Astronaut"]] = relationship(back_populates="mission")


class Astronaut(Base):
    """Profil créé à l'avance par l'équipe. L'astronaute accède à ses données avec access_code seul."""
    __tablename__ = "astronauts"

    id: Mapped[int] = mapped_column(primary_key=True)
    access_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    last_name: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(100))
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    mission: Mapped[Mission] = relationship(back_populates="astronauts")


class Indicator(Base):
    """Catalogue : unité attendue, plage plausible (rejet des aberrations) et plage normale (affichage)."""
    __tablename__ = "indicators"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(20))  # physiological | behavioral | psychological
    min_plausible: Mapped[float] = mapped_column(Float)
    max_plausible: Mapped[float] = mapped_column(Float)
    normal_min: Mapped[float | None] = mapped_column(Float)
    normal_max: Mapped[float | None] = mapped_column(Float)
    norm_reference: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[str] = mapped_column(String(2), default="P1")


class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = (Index("ix_meas_astro_ind_time", "astronaut_id", "indicator_code", "recorded_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronauts.id"))
    indicator_code: Mapped[str] = mapped_column(ForeignKey("indicators.code"))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    recorded_at: Mapped[datetime] = mapped_column(UTCDateTime)
    source: Mapped[DataSource] = mapped_column(Enum(DataSource, native_enum=False))
    source_reference: Mapped[str | None] = mapped_column(String(300))
    mission_day: Mapped[int | None] = mapped_column(Integer)
    injected: Mapped[bool] = mapped_column(Boolean, default=False)  # créée par la page de simulation
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    astronaut: Mapped[Astronaut] = relationship()
    indicator: Mapped[Indicator] = relationship()


class AlertRule(Base):
    """Règle d'alerte configurable. is_demo=True : seuil choisi par l'équipe, pas une norme publiée."""
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    indicator_code: Mapped[str] = mapped_column(ForeignKey("indicators.code"))
    operator: Mapped[Operator] = mapped_column(Enum(Operator, native_enum=False))
    threshold: Mapped[float] = mapped_column(Float)
    consecutive: Mapped[int] = mapped_column(Integer, default=1)  # persistance : nb de mesures consécutives
    level: Mapped[AlertLevel] = mapped_column(Enum(AlertLevel, native_enum=False))
    message: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    reference: Mapped[str | None] = mapped_column(String(300))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronauts.id"), index=True)
    measurement_id: Mapped[int] = mapped_column(ForeignKey("measurements.id"))
    rule_id: Mapped[str] = mapped_column(ForeignKey("alert_rules.id"))
    indicator_code: Mapped[str] = mapped_column(ForeignKey("indicators.code"))
    level: Mapped[AlertLevel] = mapped_column(Enum(AlertLevel, native_enum=False))
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus, native_enum=False), default=AlertStatus.active)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    source: Mapped[DataSource] = mapped_column(Enum(DataSource, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    measurement: Mapped[Measurement] = relationship()
    rule: Mapped[AlertRule] = relationship()

    @property
    def rule_condition(self) -> str:
        r = self.rule
        n = f" sur {r.consecutive} mesures consécutives" if r.consecutive > 1 else ""
        return f"valeur {r.operator.value} {r.threshold:g} {self.unit}{n}"

    @property
    def rule_reference(self) -> str | None:
        return self.rule.reference

    @property
    def rule_is_team_threshold(self) -> bool:
        return self.rule.is_demo
