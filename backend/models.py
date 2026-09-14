from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(String, nullable=False)
    location = Column(String, nullable=False)

    worker = relationship(
        "Worker",
        back_populates="user",
        uselist=False
    )


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)

    workers = relationship(
        "Worker",
        back_populates="service"
    )


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    name = Column(String, nullable=False)
    skills = Column(String, nullable=False)

    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    rating = Column(Float, default=0.0)
    completed_jobs = Column(Integer, default=0)

    availability = Column(Boolean, default=True)

    verification_status = Column(String, default="verified")
    reliability_score = Column(Float, default=0.0)

    user = relationship(
        "User",
        back_populates="worker"
    )

    service = relationship(
        "Service",
        back_populates="workers"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id"),
        nullable=False
    )

    status = Column(
        String,
        default="requested"
    )

    location = Column(String, nullable=False)

    scheduled_time = Column(
        String,
        nullable=False
    )

    estimated_price = Column(Float, nullable=False)
    final_price = Column(Float, nullable=True)

    is_emergency = Column(
    Boolean,
    default=False,
    nullable=False
)

    created_at = Column(
    DateTime,
    default=datetime.utcnow
)

    
class BookingWorker(Base):
    __tablename__ = "booking_workers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False
    )

    role = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)
    worker_amount = Column(Float, nullable=False)
    cooperative_amount = Column(Float, nullable=False)
    platform_amount = Column(Float, nullable=False)

    status = Column(
        String,
        default="pending"
    )


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False
    )

    rating = Column(Float, nullable=False)
    feedback = Column(String, nullable=True)
class WorkerCertification(Base):
    __tablename__ = "worker_certifications"

    id = Column(Integer, primary_key=True, index=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False
    )

    certificate_name = Column(
        String,
        nullable=False
    )

    issuing_authority = Column(
        String,
        nullable=False
    )

    certificate_id = Column(
        String,
        nullable=True
    )

    issue_date = Column(
        String,
        nullable=True
    )

    expiry_date = Column(
        String,
        nullable=True
    )

    verification_status = Column(
        String,
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
class WorkerWelfare(Base):
    __tablename__ = "worker_welfare"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id"),
        nullable=False
    )

    insurance_enrolled = Column(
        Boolean,
        default=False,
        nullable=False
    )

    insurance_provider = Column(
        String,
        nullable=True
    )

    policy_number = Column(
        String,
        nullable=True
    )

    coverage_amount = Column(
        Float,
        nullable=True
    )

    policy_start_date = Column(
        String,
        nullable=True
    )

    policy_end_date = Column(
        String,
        nullable=True
    )

    welfare_status = Column(
        String,
        default="active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )