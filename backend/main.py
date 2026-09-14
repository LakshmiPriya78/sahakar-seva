from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.fairmatch import (
    rank_workers,
    select_team,
    generate_team_recommendation
)
from backend.ai_service import (
    analyze_request,
    create_service_plan
)
from .database import Base, engine, get_db, SessionLocal
from backend.models import (
    User,
    Service,
    Worker,
    Booking,
    BookingWorker,
    Payment,
    Rating,
    WorkerCertification,
    WorkerWelfare
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SAHAKAR SEVA",
    description="Cooperative Gig & Community Services Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "project": "SAHAKAR SEVA",
        "message": "Cooperative Gig & Community Services Platform",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.get("/debug/database")
def debug_database(db: Session = Depends(get_db)):
    return {
        "services": db.query(Service).count(),
        "workers": db.query(Worker).count()
    }
@app.get("/services")
def get_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()

    return [
        {
            "id": service.id,
            "name": service.name,
            "category": service.category,
            "base_price": service.base_price
        }
        for service in services
    ]
@app.post("/workers/register")
def register_worker(request: dict):
    name = request.get("name", "").strip()
    phone = request.get("phone", "").strip()
    service_id = request.get("service_id")
    skills = request.get("skills", "").strip()
    location = request.get("location", "").strip()
    latitude = request.get("latitude")
    longitude = request.get("longitude")

    # Validate required fields
    if not name:
        return {
            "success": False,
            "message": "Worker name is required."
        }

    if not phone:
        return {
            "success": False,
            "message": "Phone number is required."
        }

    if not service_id:
        return {
            "success": False,
            "message": "Service ID is required."
        }

    if not skills:
        return {
            "success": False,
            "message": "Worker skills are required."
        }

    if not location:
        return {
            "success": False,
            "message": "Worker location is required."
        }

    if latitude is None or longitude is None:
        return {
            "success": False,
            "message": "Worker latitude and longitude are required."
        }

    db = SessionLocal()

    try:
        # Check service
        service = db.query(Service).filter(
            Service.id == service_id
        ).first()

        if not service:
            return {
                "success": False,
                "message": "Service not found."
            }

        # Check whether phone is already registered
        existing_user = db.query(User).filter(
            User.phone == phone
        ).first()

        if existing_user:
            return {
                "success": False,
                "message": "A user with this phone number already exists."
            }

        # Create worker user account
        user = User(
            name=name,
            phone=phone,
            role="worker",
            location=location
        )

        db.add(user)
        db.flush()

        # Create worker profile
        worker = Worker(
            user_id=user.id,
            service_id=service.id,
            name=name,
            skills=skills,
            location=location,
            latitude=float(latitude),
            longitude=float(longitude),
            rating=0.0,
            completed_jobs=0,
            availability=False,
            verification_status="pending",
            reliability_score=0.0
        )

        db.add(worker)
        db.commit()
        db.refresh(worker)

        return {
            "success": True,
            "message": (
                "Worker registration submitted successfully. "
                "Awaiting cooperative verification."
            ),
            "worker": {
                "id": worker.id,
                "user_id": user.id,
                "name": worker.name,
                "service": service.name,
                "skills": worker.skills,
                "location": worker.location,
                "latitude": worker.latitude,
                "longitude": worker.longitude,
                "verification_status": worker.verification_status,
                "availability": worker.availability
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Worker registration failed.",
            "error": str(e)
        }

    finally:
        db.close()
@app.post("/workers/{worker_id}/certifications")
def add_worker_certification(
    worker_id: int,
    request: dict
):
    certificate_name = request.get(
        "certificate_name",
        ""
    ).strip()

    issuing_authority = request.get(
        "issuing_authority",
        ""
    ).strip()

    certificate_id = request.get(
        "certificate_id",
        ""
    ).strip()

    issue_date = request.get(
        "issue_date",
        ""
    ).strip()

    expiry_date = request.get(
        "expiry_date",
        ""
    ).strip()

    db = SessionLocal()

    try:
        # Check worker
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        # Validate certificate
        if not certificate_name:
            return {
                "success": False,
                "message": "Certificate name is required."
            }

        if not issuing_authority:
            return {
                "success": False,
                "message": "Issuing authority is required."
            }

        # Create certification
        certification = WorkerCertification(
            worker_id=worker_id,
            certificate_name=certificate_name,
            issuing_authority=issuing_authority,
            certificate_id=certificate_id or None,
            issue_date=issue_date or None,
            expiry_date=expiry_date or None,
            verification_status="pending"
        )

        db.add(certification)
        db.commit()
        db.refresh(certification)

        return {
            "success": True,
            "message": (
                "Certification submitted successfully. "
                "Awaiting cooperative verification."
            ),
            "certification": {
                "id": certification.id,
                "worker_id": certification.worker_id,
                "certificate_name": (
                    certification.certificate_name
                ),
                "issuing_authority": (
                    certification.issuing_authority
                ),
                "certificate_id": (
                    certification.certificate_id
                ),
                "issue_date": certification.issue_date,
                "expiry_date": certification.expiry_date,
                "verification_status": (
                    certification.verification_status
                )
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Certification submission failed.",
            "error": str(e)
        }

    finally:
        db.close()
@app.get("/workers")
def get_workers(db: Session = Depends(get_db)):
    workers = db.query(Worker).all()

    return [
        {
            "id": worker.id,
            "name": worker.name,
            "service": worker.service.name,
            "skills": worker.skills,
            "location": worker.location,
            "rating": worker.rating,
            "completed_jobs": worker.completed_jobs,
            "availability": worker.availability,
            "verification_status": worker.verification_status,
            "reliability_score": worker.reliability_score
        }
        for worker in workers
    ]


@app.get("/workers/{service_name}")
def get_workers_by_service(
    service_name: str,
    db: Session = Depends(get_db)
):
    workers = (
        db.query(Worker)
        .join(Service)
        .filter(Service.name.ilike(service_name))
        .filter(Worker.availability == True)
        .all()
    )

    return [
        {
            "id": worker.id,
            "name": worker.name,
            "service": worker.service.name,
            "skills": worker.skills,
            "location": worker.location,
            "rating": worker.rating,
            "completed_jobs": worker.completed_jobs,
            "availability": worker.availability,
            "verification_status": worker.verification_status,
            "reliability_score": worker.reliability_score
        }
        for worker in workers
    ]
@app.post("/ai/analyze-request")
def analyze_customer_request(request: dict):

    request_text = request.get("request", "").strip()
    language = request.get("language", "English")

    if not request_text:

        return {
            "success": False,
            "message": "Request cannot be empty."
        }

    result = analyze_request(
        request_text,
        language
    )

    return {
        "success": True,
        "analysis": result
    }
@app.post("/ai/match-workers")
def match_workers(request: dict):

    service_name = (request.get("service") or "").strip()
    problem = request.get("problem")
    customer_lat = request.get("latitude")
    customer_lon = request.get("longitude")

    if not service_name:
        return {
            "success": False,
            "message": "Service is required."
        }

    if customer_lat is None or customer_lon is None:
        return {
            "success": False,
            "message": "Customer location is required."
        }

    db = SessionLocal()

    try:

        workers = (
            db.query(Worker)
            .join(Service)
            .filter(
                Service.name == service_name,
                Worker.availability == True
            )
            .all()
        )

        worker_data = []

        for worker in workers:

            worker_data.append({
                "id": worker.id,
                "name": worker.name,
                "skills": worker.skills,
                "latitude": worker.latitude,
                "longitude": worker.longitude,
                "rating": worker.rating,
                "completed_jobs": worker.completed_jobs,
                "availability": worker.availability,
                "reliability_score": worker.reliability_score
            })

        ranked_workers = rank_workers(
            worker_data,
            float(customer_lat),
            float(customer_lon),
            problem
        )

        return {
            "success": True,
            "service": service_name,
            "problem": problem,
            "workers_found": len(ranked_workers),
            "matches": ranked_workers
        }

    finally:

        db.close()

@app.post("/bookings")
def create_booking(request: dict):
    customer_id = request.get("customer_id")
    worker_id = request.get("worker_id")
    service_name = request.get("service")
    location = request.get("location")
    scheduled_time = request.get("scheduled_time")
    estimated_price = request.get("estimated_price")
    is_emergency = request.get("is_emergency", False)

    if not customer_id:
        return {
            "success": False,
            "message": "Customer ID is required."
        }

    if not worker_id:
        return {
            "success": False,
            "message": "Worker ID is required."
        }

    if not service_name:
        return {
            "success": False,
            "message": "Service is required."
        }

    db = SessionLocal()

    try:

        # Find customer
        customer = db.query(User).filter(
            User.id == customer_id
        ).first()

        if not customer:
            return {
                "success": False,
                "message": "Customer not found."
            }

        # Find worker
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        # Find service
        service = db.query(Service).filter(
            Service.name == service_name
        ).first()

        if not service:
            return {
                "success": False,
                "message": "Service not found."
            }

        # Check worker availability
        if worker.availability is not True:
            return {
                "success": False,
                "message": "Worker is currently unavailable."
            }

        # Create booking
        booking = Booking(
            customer_id=customer_id,
            worker_id=worker_id,
            service_id=service.id,
            status="requested",
            location=location,
            scheduled_time=scheduled_time,
            estimated_price=estimated_price,
            is_emergency=is_emergency
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return {
            "success": True,
            "message": "Booking created successfully.",
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
                "worker_id": booking.worker_id,
                "worker_name": worker.name,
                "service": service.name,
                "status": booking.status,
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "estimated_price": booking.estimated_price,
                "is_emergency": booking.is_emergency
            }
        }

    finally:
        db.close()
@app.put("/bookings/{booking_id}/respond")
def respond_to_booking(booking_id: int, request: dict):

    response = request.get("response", "").strip().lower()

    if response not in ["accepted", "rejected"]:
        return {
            "success": False,
            "message": "Response must be either 'accepted' or 'rejected'."
        }

    db = SessionLocal()

    try:

        # Find booking
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        # Booking must still be requested
        if booking.status != "requested":
            return {
                "success": False,
                "message": (
                    f"Booking cannot be responded to because "
                    f"its current status is '{booking.status}'."
                )
            }

        # Update booking status
        booking.status = response

        db.commit()
        db.refresh(booking)

        return {
            "success": True,
            "message": f"Booking {response} successfully.",
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
                "worker_id": booking.worker_id,
                "service_id": booking.service_id,
                "status": booking.status,
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "estimated_price": booking.estimated_price
            }
        }

    finally:
        db.close()

@app.put("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, request: dict):

    new_status = request.get("status", "").strip().lower()

    allowed_transitions = {
        "accepted": ["on_the_way"],
        "on_the_way": ["arrived"],
        "arrived": ["in_progress"],
        "in_progress": ["completed"]
    }

    db = SessionLocal()

    try:
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        current_status = booking.status

        if current_status not in allowed_transitions:
            return {
                "success": False,
                "message": (
                    f"Booking cannot move from "
                    f"'{current_status}'."
                )
            }

        if new_status not in allowed_transitions[current_status]:
            return {
                "success": False,
                "message": (
                    f"Invalid status transition: "
                    f"'{current_status}' → '{new_status}'."
                )
            }

        booking.status = new_status

        db.commit()
        db.refresh(booking)

        return {
            "success": True,
            "message": (
                f"Booking status updated from "
                f"'{current_status}' to '{new_status}'."
            ),
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
                "worker_id": booking.worker_id,
                "service_id": booking.service_id,
                "status": booking.status,
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "estimated_price": booking.estimated_price
            }
        }

    finally:
        db.close()

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):
    db = SessionLocal()

    try:
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        service = db.query(Service).filter(
            Service.id == booking.service_id
        ).first()

        worker = db.query(Worker).filter(
            Worker.id == booking.worker_id
        ).first()

        return {
            "success": True,
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
                "worker_id": booking.worker_id,
                "worker_name": (
                    worker.name
                    if worker
                    else "Unknown"
                ),
                "service": (
                    service.name
                    if service
                    else "Unknown"
                ),
                "status": booking.status,
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "estimated_price": booking.estimated_price,
                "final_price": booking.final_price
            }
        }

    finally:
        db.close()
        
@app.get("/bookings/worker/{worker_id}")
def get_worker_bookings(worker_id: int):

    db = SessionLocal()

    try:
        bookings = db.query(Booking).filter(
            Booking.worker_id == worker_id
        ).order_by(
            Booking.id.desc()
        ).all()

        results = []

        for booking in bookings:

            service = db.query(Service).filter(
                Service.id == booking.service_id
            ).first()

            results.append({
                "id": booking.id,
                "customer_id": booking.customer_id,
                "worker_id": booking.worker_id,
                "service": service.name if service else "Unknown",
                "status": booking.status,
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "estimated_price": booking.estimated_price
            })

        return {
            "success": True,
            "worker_id": worker_id,
            "bookings": results
        }

    finally:
        db.close()

@app.get("/workers/{worker_id}/profile")
def get_worker_profile(worker_id: int):
    db = SessionLocal()

    try:
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        service = db.query(Service).filter(
            Service.id == worker.service_id
        ).first()

        # Calculate actual completed jobs from booking history
        completed_jobs = db.query(Booking).filter(
            Booking.worker_id == worker_id,
            Booking.status == "completed"
        ).count()

        return {
            "success": True,
            "worker": {
                "id": worker.id,
                "name": worker.name,
                "service": service.name if service else "Unknown",
                "skills": worker.skills,
                "location": worker.location,
                "rating": worker.rating,

                # Actual SAHAKAR SEVA completed jobs
                "completed_jobs": completed_jobs,

                "availability": worker.availability,
                "verification_status": worker.verification_status,
                "reliability_score": worker.reliability_score
            }
        }

    finally:
        db.close()

@app.put("/workers/{worker_id}/availability")
def update_worker_availability(
    worker_id: int,
    request: dict
):

    availability = request.get("availability")

    if not isinstance(availability, bool):

        return {
            "success": False,
            "message": (
                "Availability must be true or false."
            )
        }

    db = SessionLocal()

    try:

        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:

            return {
                "success": False,
                "message": "Worker not found."
            }

        worker.availability = availability

        db.commit()
        db.refresh(worker)

        return {
            "success": True,
            "message": (
                "Worker availability updated successfully."
            ),
            "worker": {
                "id": worker.id,
                "name": worker.name,
                "availability": worker.availability
            }
        }

    finally:

        db.close()

@app.get("/workers/{worker_id}/earnings")
def get_worker_earnings(worker_id: int):

    db = SessionLocal()

    try:
        # Find worker
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        # Find completed bookings
        completed_bookings = db.query(Booking).filter(
            Booking.worker_id == worker_id,
            Booking.status == "completed"
        ).all()

        total_earnings = 0.0
        paid_jobs = 0

        for booking in completed_bookings:

            # Find payment for this booking
            payment = db.query(Payment).filter(
                Payment.booking_id == booking.id
            ).first()

            if payment:
                total_earnings += payment.worker_amount

                if payment.status == "paid":
                    paid_jobs += 1

        return {
            "success": True,
            "worker_id": worker_id,
            "worker_name": worker.name,
            "completed_jobs": len(completed_bookings),
            "paid_jobs": paid_jobs,
            "total_earnings": round(total_earnings, 2)
        }

    finally:
        db.close()
@app.get("/cooperative/dashboard")
def get_cooperative_dashboard():
    db = SessionLocal()

    try:
        total_workers = db.query(Worker).count()

        active_workers = db.query(Worker).filter(
            Worker.availability == True
        ).count()

        total_bookings = db.query(Booking).count()

        completed_bookings = db.query(Booking).filter(
            Booking.status == "completed"
        ).count()

        active_bookings = db.query(Booking).filter(
            Booking.status.in_([
                "accepted",
                "on_the_way",
                "arrived",
                "in_progress"
            ])
        ).count()

        requested_bookings = db.query(Booking).filter(
            Booking.status == "requested"
        ).count()

        total_worker_earnings = 0.0

        payments = db.query(Payment).all()

        for payment in payments:
            total_worker_earnings += payment.worker_amount

        service_demand = {}

        bookings = db.query(Booking).all()

        for booking in bookings:

            service = db.query(Service).filter(
                Service.id == booking.service_id
            ).first()

            if service:

                service_name = service.name

                if service_name not in service_demand:
                    service_demand[service_name] = 0

                service_demand[service_name] += 1

        return {
            "success": True,
            "dashboard": {
                "total_workers": total_workers,
                "active_workers": active_workers,
                "total_bookings": total_bookings,
                "completed_bookings": completed_bookings,
                "active_bookings": active_bookings,
                "requested_bookings": requested_bookings,
                "total_worker_earnings": round(
                    total_worker_earnings,
                    2
                ),
                "service_demand": service_demand
            }
        }

    finally:
        db.close()
@app.get("/cooperative/workforce-intelligence")
def get_workforce_intelligence():

    db = SessionLocal()

    try:

        services = db.query(Service).all()

        intelligence = []

        for service in services:

            total_workers = db.query(Worker).filter(
                Worker.service_id == service.id
            ).count()

            available_workers = db.query(Worker).filter(
                Worker.service_id == service.id,
                Worker.availability == True
            ).count()

            total_bookings = db.query(Booking).filter(
                Booking.service_id == service.id
            ).count()

            active_bookings = db.query(Booking).filter(
                Booking.service_id == service.id,
                Booking.status.in_([
                    "requested",
                    "accepted",
                    "on_the_way",
                    "arrived",
                    "in_progress"
                ])
            ).count()

            completed_bookings = db.query(Booking).filter(
                Booking.service_id == service.id,
                Booking.status == "completed"
            ).count()

            # -------------------------------------------------
            # CAPACITY LOAD
            # -------------------------------------------------

            if available_workers > 0:

                capacity_load = (
                    active_bookings / available_workers
                ) * 100

            else:

                capacity_load = (
                    100 if active_bookings > 0 else 0
                )

            # -------------------------------------------------
            # WORKFORCE INTELLIGENCE
            # -------------------------------------------------

            if total_workers == 0:

                workforce_status = "Critical Gap"

                recommendation = (
                    f"No {service.name} workers are currently "
                    f"registered. The cooperative should begin "
                    f"worker onboarding for this service."
                )

                recommended_action = (
                    f"Onboard {service.name} workers"
                )

            elif available_workers == 0 and active_bookings > 0:

                workforce_status = "Critical Gap"

                recommendation = (
                    f"No {service.name} workers are currently "
                    f"available while there are active requests. "
                    f"The cooperative should immediately increase "
                    f"workforce availability."
                )

                recommended_action = (
                    f"Activate or onboard available "
                    f"{service.name} workers"
                )

            elif capacity_load >= 100:

                workforce_status = "Workforce Gap"

                recommendation = (
                    f"{service.name} workforce is operating at "
                    f"full capacity. The cooperative should "
                    f"consider increasing available workforce."
                )

                recommended_action = (
                    f"Onboard or activate additional "
                    f"{service.name} workers"
                )

            elif capacity_load >= 70:

                workforce_status = "High Utilization"

                recommendation = (
                    f"{service.name} workforce utilization is high. "
                    f"The cooperative should monitor upcoming demand "
                    f"and workforce availability."
                )

                recommended_action = (
                    f"Monitor and prepare additional "
                    f"{service.name} capacity"
                )

            else:

                workforce_status = "Adequate"

                recommendation = (
                    f"Current {service.name} workforce appears "
                    f"adequate. Continue monitoring demand."
                )

                recommended_action = (
                    f"Continue monitoring {service.name} demand"
                )
                # Demand vs Workforce comparison
            if total_workers > 0:
              demand_per_worker = total_bookings / total_workers
            else:
             demand_per_worker = total_bookings
            # Priority level
            if capacity_load >= 100 and demand_per_worker >= 5:
              priority_level = "High Priority"

            elif capacity_load >= 70 or demand_per_worker >= 5:
               priority_level = "Medium Priority"

            else:
                 priority_level = "Normal"
            if total_workers == 0 and total_bookings > 0:
               demand_status = "Unserved Demand"

            elif demand_per_worker >= 5:
              demand_status = "High Historical Demand"

            elif demand_per_worker > 0:
              demand_status = "Moderate Historical Demand"

            else:
              demand_status = "No Recorded Demand"

            # -------------------------------------------------
            # ADD SERVICE INTELLIGENCE
            # -------------------------------------------------

            intelligence.append({
                "service": service.name,
                "priority_level": priority_level,
                "total_workers": total_workers,
                "available_workers": available_workers,
                "total_bookings": total_bookings,
                "active_bookings": active_bookings,
                "completed_bookings": completed_bookings,
                "capacity_load": round(capacity_load, 1),
                "demand_per_worker": round(demand_per_worker, 1),
                "demand_status": demand_status,
                "workforce_status": workforce_status,
                "recommendation": recommendation,
                "recommended_action": recommended_action
            })

        return {
            "success": True,
            "intelligence": intelligence
        }

    finally:

        db.close()
@app.get("/cooperative/workers/welfare")
def get_cooperative_worker_welfare():
    db = SessionLocal()

    try:
        workers = db.query(Worker).all()

        worker_welfare = []

        for worker in workers:
            welfare = db.query(WorkerWelfare).filter(
                WorkerWelfare.worker_id == worker.id
            ).first()

            worker_welfare.append({
                "worker_id": worker.id,
                "worker_name": worker.name,
                "insurance_enrolled": (
                    welfare.insurance_enrolled
                    if welfare else False
                ),
                "insurance_provider": (
                    welfare.insurance_provider
                    if welfare else None
                ),
                "policy_number": (
                    welfare.policy_number
                    if welfare else None
                ),
                "coverage_amount": (
                    welfare.coverage_amount
                    if welfare else None
                ),
                "policy_start_date": (
                    welfare.policy_start_date
                    if welfare else None
                ),
                "policy_end_date": (
                    welfare.policy_end_date
                    if welfare else None
                ),
                "welfare_status": (
                    welfare.welfare_status
                    if welfare else "not_registered"
                )
            })

        return {
            "success": True,
            "count": len(worker_welfare),
            "workers": worker_welfare
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to retrieve worker welfare information.",
            "error": str(e)
        }

    finally:
        db.close()
# ============================================================
# COOPERATIVE WORKER VERIFICATION
# ============================================================

@app.get("/cooperative/workers/pending")
def get_pending_workers():
    db = SessionLocal()

    try:
        workers = db.query(Worker).filter(
            Worker.verification_status == "pending"
        ).all()

        pending_workers = []

        for worker in workers:

            service = db.query(Service).filter(
                Service.id == worker.service_id
            ).first()

            pending_workers.append({
                "worker_id": worker.id,
                "user_id": worker.user_id,
                "name": worker.name,
                "service": service.name if service else "Unknown",
                "skills": worker.skills,
                "location": worker.location,
                "latitude": worker.latitude,
                "longitude": worker.longitude,
                "verification_status": worker.verification_status,
                "availability": worker.availability
            })

        return {
            "success": True,
            "count": len(pending_workers),
            "pending_workers": pending_workers
        }

    finally:
        db.close()


@app.post("/cooperative/workers/{worker_id}/approve")
def approve_worker(worker_id: int):
    db = SessionLocal()

    try:
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        if worker.verification_status != "pending":
            return {
                "success": False,
                "message": (
                    f"Worker is already "
                    f"{worker.verification_status}."
                )
            }

        worker.verification_status = "verified"
        worker.availability = True

        db.commit()
        db.refresh(worker)

        return {
            "success": True,
            "message": (
                "Worker approved successfully. "
                "Worker is now verified and available."
            ),
            "worker": {
                "worker_id": worker.id,
                "name": worker.name,
                "verification_status": worker.verification_status,
                "availability": worker.availability
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Worker approval failed.",
            "error": str(e)
        }

    finally:
        db.close()


@app.post("/cooperative/workers/{worker_id}/reject")
def reject_worker(worker_id: int):
    db = SessionLocal()

    try:
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        if worker.verification_status != "pending":
            return {
                "success": False,
                "message": (
                    f"Worker is already "
                    f"{worker.verification_status}."
                )
            }

        worker.verification_status = "rejected"
        worker.availability = False

        db.commit()
        db.refresh(worker)

        return {
            "success": True,
            "message": "Worker registration rejected.",
            "worker": {
                "worker_id": worker.id,
                "name": worker.name,
                "verification_status": worker.verification_status,
                "availability": worker.availability
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Worker rejection failed.",
            "error": str(e)
        }

    finally:
        db.close()
# ============================================================
# COOPERATIVE CERTIFICATION VERIFICATION
# ============================================================

@app.get("/cooperative/certifications/pending")
def get_pending_certifications():
    db = SessionLocal()

    try:
        certifications = db.query(WorkerCertification).filter(
            WorkerCertification.verification_status == "pending"
        ).all()

        pending_certifications = []

        for certification in certifications:

            worker = db.query(Worker).filter(
                Worker.id == certification.worker_id
            ).first()

            pending_certifications.append({
                "certification_id": certification.id,
                "worker_id": certification.worker_id,
                "worker_name": worker.name if worker else "Unknown",
                "certificate_name": certification.certificate_name,
                "issuing_authority": certification.issuing_authority,
                "certificate_id": certification.certificate_id,
                "issue_date": certification.issue_date,
                "expiry_date": certification.expiry_date,
                "verification_status": certification.verification_status
            })

        return {
            "success": True,
            "count": len(pending_certifications),
            "pending_certifications": pending_certifications
        }

    finally:
        db.close()


@app.post("/cooperative/certifications/{certification_id}/approve")
def approve_certification(certification_id: int):
    db = SessionLocal()

    try:
        certification = db.query(
            WorkerCertification
        ).filter(
            WorkerCertification.id == certification_id
        ).first()

        if not certification:
            return {
                "success": False,
                "message": "Certification not found."
            }

        if certification.verification_status != "pending":
            return {
                "success": False,
                "message": (
                    f"Certification is already "
                    f"{certification.verification_status}."
                )
            }

        certification.verification_status = "verified"

        db.commit()
        db.refresh(certification)

        return {
            "success": True,
            "message": "Certification approved successfully.",
            "certification": {
                "certification_id": certification.id,
                "worker_id": certification.worker_id,
                "certificate_name": certification.certificate_name,
                "verification_status": certification.verification_status
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Certification approval failed.",
            "error": str(e)
        }

    finally:
        db.close()


@app.post("/cooperative/certifications/{certification_id}/reject")
def reject_certification(certification_id: int):
    db = SessionLocal()

    try:
        certification = db.query(
            WorkerCertification
        ).filter(
            WorkerCertification.id == certification_id
        ).first()

        if not certification:
            return {
                "success": False,
                "message": "Certification not found."
            }

        if certification.verification_status != "pending":
            return {
                "success": False,
                "message": (
                    f"Certification is already "
                    f"{certification.verification_status}."
                )
            }

        certification.verification_status = "rejected"

        db.commit()
        db.refresh(certification)

        return {
            "success": True,
            "message": "Certification rejected.",
            "certification": {
                "certification_id": certification.id,
                "worker_id": certification.worker_id,
                "certificate_name": certification.certificate_name,
                "verification_status": certification.verification_status
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Certification rejection failed.",
            "error": str(e)
        }

    finally:
        db.close()
@app.post("/workers/{worker_id}/welfare")
def add_worker_welfare(worker_id: int, request: dict):
    insurance_enrolled = request.get("insurance_enrolled", False)
    insurance_provider = request.get("insurance_provider", "").strip()
    policy_number = request.get("policy_number", "").strip()
    coverage_amount = request.get("coverage_amount")
    policy_start_date = request.get("policy_start_date", "").strip()
    policy_end_date = request.get("policy_end_date", "").strip()

    db = SessionLocal()

    try:
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        existing_welfare = db.query(WorkerWelfare).filter(
            WorkerWelfare.worker_id == worker_id
        ).first()

        if existing_welfare:
            existing_welfare.insurance_enrolled = insurance_enrolled
            existing_welfare.insurance_provider = insurance_provider or None
            existing_welfare.policy_number = policy_number or None
            existing_welfare.coverage_amount = coverage_amount
            existing_welfare.policy_start_date = policy_start_date or None
            existing_welfare.policy_end_date = policy_end_date or None

            db.commit()
            db.refresh(existing_welfare)

            return {
                "success": True,
                "message": "Worker welfare information updated successfully.",
                "welfare": {
                    "id": existing_welfare.id,
                    "worker_id": existing_welfare.worker_id,
                    "insurance_enrolled": existing_welfare.insurance_enrolled,
                    "insurance_provider": existing_welfare.insurance_provider,
                    "policy_number": existing_welfare.policy_number,
                    "coverage_amount": existing_welfare.coverage_amount,
                    "policy_start_date": existing_welfare.policy_start_date,
                    "policy_end_date": existing_welfare.policy_end_date,
                    "welfare_status": existing_welfare.welfare_status
                }
            }

        welfare = WorkerWelfare(
            worker_id=worker_id,
            insurance_enrolled=insurance_enrolled,
            insurance_provider=insurance_provider or None,
            policy_number=policy_number or None,
            coverage_amount=coverage_amount,
            policy_start_date=policy_start_date or None,
            policy_end_date=policy_end_date or None,
            welfare_status="active"
        )

        db.add(welfare)
        db.commit()
        db.refresh(welfare)

        return {
            "success": True,
            "message": "Worker welfare information submitted successfully.",
            "welfare": {
                "id": welfare.id,
                "worker_id": welfare.worker_id,
                "insurance_enrolled": welfare.insurance_enrolled,
                "insurance_provider": welfare.insurance_provider,
                "policy_number": welfare.policy_number,
                "coverage_amount": welfare.coverage_amount,
                "policy_start_date": welfare.policy_start_date,
                "policy_end_date": welfare.policy_end_date,
                "welfare_status": welfare.welfare_status
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Worker welfare submission failed.",
            "error": str(e)
        }

    finally:
        db.close()
@app.get("/workers/{worker_id}/welfare")
def get_worker_welfare(worker_id: int):
    db = SessionLocal()

    try:
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        welfare = db.query(WorkerWelfare).filter(
            WorkerWelfare.worker_id == worker_id
        ).first()

        if not welfare:
            return {
                "success": False,
                "message": "Welfare information not found."
            }

        return {
            "success": True,
            "welfare": {
                "id": welfare.id,
                "worker_id": welfare.worker_id,
                "insurance_enrolled": welfare.insurance_enrolled,
                "insurance_provider": welfare.insurance_provider,
                "policy_number": welfare.policy_number,
                "coverage_amount": welfare.coverage_amount,
                "policy_start_date": welfare.policy_start_date,
                "policy_end_date": welfare.policy_end_date,
                "welfare_status": welfare.welfare_status
            }
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to retrieve worker welfare information.",
            "error": str(e)
        }

    finally:
        db.close()
@app.get("/workers/{worker_id}/earnings/breakdown")
def get_worker_earnings_breakdown(worker_id: int):
    db = SessionLocal()

    try:
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        completed_bookings = db.query(Booking).filter(
            Booking.worker_id == worker_id,
            Booking.status == "completed"
        ).all()

        breakdown = []

        for booking in completed_bookings:

            service = db.query(Service).filter(
                Service.id == booking.service_id
            ).first()

            payment = db.query(Payment).filter(
                Payment.booking_id == booking.id
            ).first()

            if payment:
                worker_amount = payment.worker_amount
                payment_status = payment.status
                customer_payment = payment.amount
            else:
                worker_amount = None
                payment_status = "not_generated"
                customer_payment = None

            breakdown.append({
                "booking_id": booking.id,
                "service": service.name if service else "Unknown",
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "amount": worker_amount,
                "customer_payment": customer_payment,
                "worker_amount": worker_amount,
                "payment_status": payment_status,
                "status": booking.status
            })

        return {
            "success": True,
            "worker_id": worker_id,
            "worker_name": worker.name,
            "completed_jobs": len(completed_bookings),
            "breakdown": breakdown
        }

    finally:
        db.close()
# ============================================================
# CUSTOMER RATING & FEEDBACK
# ============================================================

@app.post("/ratings")
def submit_rating(request: dict):
    booking_id = request.get("booking_id")
    customer_id = request.get("customer_id")
    rating_value = request.get("rating")
    feedback = request.get("feedback", "").strip()

    if not booking_id:
        return {
            "success": False,
            "message": "Booking ID is required."
        }

    if not customer_id:
        return {
            "success": False,
            "message": "Customer ID is required."
        }

    if rating_value is None:
        return {
            "success": False,
            "message": "Rating is required."
        }

    try:
        rating_value = float(rating_value)
    except (TypeError, ValueError):
        return {
            "success": False,
            "message": "Rating must be a number."
        }

    if rating_value < 1 or rating_value > 5:
        return {
            "success": False,
            "message": "Rating must be between 1 and 5."
        }

    db = SessionLocal()

    try:
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        customer = db.query(User).filter(
            User.id == customer_id
        ).first()

        if not customer:
            return {
                "success": False,
                "message": "Customer not found."
            }

        if booking.customer_id != customer_id:
            return {
                "success": False,
                "message": "This customer is not associated with this booking."
            }

        if booking.status != "completed":
            return {
                "success": False,
                "message": "Rating can only be submitted after the booking is completed."
            }

        existing_rating = db.query(Rating).filter(
            Rating.booking_id == booking_id
        ).first()

        if existing_rating:
            return {
                "success": False,
                "message": "A rating already exists for this booking."
            }

        new_rating = Rating(
            booking_id=booking.id,
            customer_id=customer_id,
            worker_id=booking.worker_id,
            rating=rating_value,
            feedback=feedback or None
        )

        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)

        # ---------------------------------------------------------
        # UPDATE WORKER AVERAGE RATING
        # ---------------------------------------------------------

        worker = db.query(Worker).filter(
            Worker.id == booking.worker_id
        ).first()

        if worker:
            worker_ratings = db.query(Rating).filter(
                Rating.worker_id == worker.id
            ).all()

            if worker_ratings:
                total_rating = sum(
                    r.rating for r in worker_ratings
                )

                worker.rating = round(
                    total_rating / len(worker_ratings),
                    2
                )

                db.commit()
                db.refresh(worker)

        return {
            "success": True,
            "message": "Rating submitted successfully.",
            "rating": {
                "id": new_rating.id,
                "booking_id": new_rating.booking_id,
                "customer_id": new_rating.customer_id,
                "worker_id": new_rating.worker_id,
                "rating": new_rating.rating,
                "feedback": new_rating.feedback
            }
        }

    except Exception as e:
        db.rollback()

        return {
            "success": False,
            "message": "Rating submission failed.",
            "error": str(e)
        }

    finally:
        db.close()
@app.get("/workers/{worker_id}/bookings/{booking_id}")
def get_worker_booking_details(
    worker_id: int,
    booking_id: int
):

    db = SessionLocal()

    try:

        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:

            return {
                "success": False,
                "message": "Worker not found."
            }

        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.worker_id == worker_id
        ).first()

        if not booking:

            return {
                "success": False,
                "message": (
                    "Booking not found for this worker."
                )
            }

        service = db.query(Service).filter(
            Service.id == booking.service_id
        ).first()

        customer = db.query(User).filter(
            User.id == booking.customer_id
        ).first()

        return {
            "success": True,
            "booking": {
                "id": booking.id,
                "customer_id": booking.customer_id,
                "customer_name": (
                    customer.name
                    if customer
                    else "Unknown"
                ),
                "worker_id": booking.worker_id,
                "service": (
                    service.name
                    if service
                    else "Unknown"
                ),
                "status": booking.status,
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "estimated_price": booking.estimated_price,
                "final_price": booking.final_price
            }
        }

    finally:

        db.close()

@app.get("/workers/{worker_id}/requests")
def get_worker_requests(worker_id: int):
    db = SessionLocal()

    try:
        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }

        requests = db.query(Booking).filter(
            Booking.worker_id == worker_id,
            Booking.status == "requested"
            ).order_by(
            Booking.is_emergency.desc(),
            Booking.id.desc()
            ).all()

        request_list = []

        for booking in requests:
            service = db.query(Service).filter(
                Service.id == booking.service_id
            ).first()

            customer = db.query(User).filter(
                User.id == booking.customer_id
            ).first()

            request_list.append({
                "booking_id": booking.id,
                "customer_id": booking.customer_id,
                "customer_name": (
                    customer.name
                    if customer
                    else "Unknown"
                ),
                "service": (
                    service.name
                    if service
                    else "Unknown"
                ),
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "estimated_price": booking.estimated_price,
                "is_emergency": booking.is_emergency,
                "status": booking.status
            })

        return {
            "success": True,
            "worker_id": worker.id,
            "worker_name": worker.name,
            "request_count": len(request_list),
            "requests": request_list
        }

    finally:
        db.close()
@app.post("/payments/calculate")
def calculate_payment(request: dict):

    booking_id = request.get("booking_id")

    if not booking_id:
        return {
            "success": False,
            "message": "Booking ID is required."
        }

    db = SessionLocal()

    try:
        # Find booking
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        # Payment should only be calculated after service completion
        if booking.status != "completed":
            return {
                "success": False,
                "message": (
                    f"Payment cannot be calculated because "
                    f"booking status is '{booking.status}'."
                )
            }

        # Use final price if available, otherwise estimated price
        total_amount = (
            booking.final_price
            if booking.final_price is not None
            else booking.estimated_price
        )

        # Prototype allocation
        worker_amount = total_amount * 0.80
        cooperative_amount = total_amount * 0.15
        platform_amount = total_amount * 0.05

        return {
            "success": True,
            "payment": {
                "booking_id": booking.id,
                "total_amount": round(total_amount, 2),
                "worker_amount": round(worker_amount, 2),
                "cooperative_amount": round(cooperative_amount, 2),
                "platform_amount": round(platform_amount, 2)
            }
        }

    finally:
        db.close()
@app.post("/payments/create")
def create_payment(request: dict):

    booking_id = request.get("booking_id")

    if not booking_id:
        return {
            "success": False,
            "message": "Booking ID is required."
        }

    db = SessionLocal()

    try:
        # Find booking
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        # Payment can only be created after completion
        if booking.status != "completed":
            return {
                "success": False,
                "message": (
                    f"Payment cannot be created because "
                    f"booking status is '{booking.status}'."
                )
            }

        # Check whether payment already exists
        existing_payment = db.query(Payment).filter(
            Payment.booking_id == booking_id
        ).first()

        if existing_payment:
            return {
                "success": False,
                "message": "Payment already exists for this booking."
            }

        # Use final price if available
        total_amount = (
            booking.final_price
            if booking.final_price is not None
            else booking.estimated_price
        )

        # Prototype allocation
        worker_amount = total_amount * 0.80
        cooperative_amount = total_amount * 0.15
        platform_amount = total_amount * 0.05

        # Create payment record
        payment = Payment(
            booking_id=booking.id,
            amount=round(total_amount, 2),
            worker_amount=round(worker_amount, 2),
            cooperative_amount=round(cooperative_amount, 2),
            platform_amount=round(platform_amount, 2),
            status="pending"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {
            "success": True,
            "message": "Payment record created successfully.",
            "payment": {
                "id": payment.id,
                "booking_id": payment.booking_id,
                "amount": payment.amount,
                "worker_amount": payment.worker_amount,
                "cooperative_amount": payment.cooperative_amount,
                "platform_amount": payment.platform_amount,
                "status": payment.status
            }
        }

    finally:
        db.close()
@app.get("/payments/{payment_id}/invoice")
def get_invoice(payment_id: int):

    db = SessionLocal()

    try:
        # Find payment
        payment = db.query(Payment).filter(
            Payment.id == payment_id
        ).first()

        if not payment:
            return {
                "success": False,
                "message": "Payment not found."
            }

        # Find booking
        booking = db.query(Booking).filter(
            Booking.id == payment.booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        # Find service
        service = db.query(Service).filter(
            Service.id == booking.service_id
        ).first()

        # Find worker
        worker = db.query(Worker).filter(
            Worker.id == booking.worker_id
        ).first()

        return {
            "success": True,
            "invoice": {
                "invoice_id": f"INV-{payment.id:04d}",
                "payment_id": payment.id,
                "booking_id": booking.id,

                "service": service.name if service else "Unknown",
                "worker": worker.name if worker else "Unknown",

                "location": booking.location,
                "scheduled_time": booking.scheduled_time,

                "total_amount": payment.amount,
                "worker_amount": payment.worker_amount,
                "cooperative_amount": payment.cooperative_amount,
                "platform_amount": payment.platform_amount,

                "payment_status": payment.status
            }
        }

    finally:
        db.close()
@app.get("/bookings/{booking_id}/invoice")
def get_booking_invoice(booking_id: int):

    db = SessionLocal()

    try:
        # Find payment for this booking
        payment = db.query(Payment).filter(
            Payment.booking_id == booking_id
        ).first()

        if not payment:
            return {
                "success": False,
                "message": "Payment record not found for this booking."
            }

        # Find booking
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        # Find service
        service = db.query(Service).filter(
            Service.id == booking.service_id
        ).first()

        # Find worker
        worker = db.query(Worker).filter(
            Worker.id == booking.worker_id
        ).first()

        return {
            "success": True,
            "invoice": {
                "invoice_id": f"INV-{payment.id:04d}",
                "payment_id": payment.id,
                "booking_id": booking.id,
                "service": service.name if service else "Unknown",
                "worker": worker.name if worker else "Unknown",
                "location": booking.location,
                "scheduled_time": booking.scheduled_time,
                "total_amount": payment.amount,
                "worker_amount": payment.worker_amount,
                "cooperative_amount": payment.cooperative_amount,
                "platform_amount": payment.platform_amount,
                "payment_status": payment.status
            }
        }

    finally:
        db.close()
@app.get("/cooperative/demand-forecast")
def get_demand_forecast():

    db = SessionLocal()

    try:

        services = db.query(Service).all()

        forecasts = []

        for service in services:

            total_workers = db.query(Worker).filter(
                Worker.service_id == service.id
            ).count()

            available_workers = db.query(Worker).filter(
                Worker.service_id == service.id,
                Worker.availability == True
            ).count()

            total_bookings = db.query(Booking).filter(
                Booking.service_id == service.id
            ).count()

            active_bookings = db.query(Booking).filter(
                Booking.service_id == service.id,
                Booking.status.in_([
                    "requested",
                    "accepted",
                    "on_the_way",
                    "arrived",
                    "in_progress"
                ])
            ).count()

            if total_workers > 0:
                demand_per_worker = (
                    total_bookings / total_workers
                )
            else:
                demand_per_worker = total_bookings

            # Baseline forecast
            estimated_demand = total_bookings

            # Current workforce capacity
            if available_workers > 0:
                capacity_load = (
                    active_bookings / available_workers
                ) * 100
            else:
                capacity_load = (
                    100 if active_bookings > 0 else 0
                )

            # Forecast status
            if estimated_demand >= 10:
                forecast_status = "High Demand"

            elif estimated_demand > 0:
                forecast_status = "Moderate Demand"

            else:
                forecast_status = "No Recorded Demand"

            # Forecast-based workforce recommendation
            if (
                forecast_status == "High Demand"
                and capacity_load >= 100
            ):
                workforce_recommendation = (
                    f"Urgently onboard or activate additional "
                    f"{service.name} workers."
                )

            elif (
                forecast_status == "High Demand"
                and capacity_load >= 70
            ):
                workforce_recommendation = (
                    f"Prepare additional {service.name} "
                    f"workforce capacity."
                )

            elif forecast_status == "High Demand":
                workforce_recommendation = (
                    f"Plan additional {service.name} "
                    f"workforce for upcoming demand."
                )

            elif forecast_status == "Moderate Demand":
                workforce_recommendation = (
                    f"Monitor {service.name} demand and "
                    f"workforce availability."
                )

            else:
                workforce_recommendation = (
                    f"Continue monitoring {service.name} "
                    f"before expanding workforce."
                )

            forecasts.append({
                "service": service.name,
                "historical_bookings": total_bookings,
                "total_workers": total_workers,
                "available_workers": available_workers,
                "active_bookings": active_bookings,
                "demand_per_worker": round(
                    demand_per_worker, 1
                ),
                "estimated_next_period_demand": estimated_demand,
                "capacity_load": round(
                    capacity_load, 1
                ),
                "forecast_status": forecast_status,
                "workforce_recommendation":
                    workforce_recommendation
            })

        return {
            "success": True,
            "forecast": forecasts
        }

    finally:
        db.close()
@app.post("/ai/match-team")
def match_complex_team(request: dict):

    request_text = request.get(
        "request",
        ""
    ).strip()

    customer_lat = request.get(
        "customer_lat",
        13.6288
    )

    customer_lon = request.get(
        "customer_lon",
        79.4192
    )

    if not request_text:

        return {
            "success": False,
            "message": "Request cannot be empty."
        }

    analysis = analyze_request(
        request_text
    )

    if analysis.get("request_type") != "complex_service":

        return {
            "success": False,
            "message": "This request does not require team matching."
        }

    team_size = analysis.get(
        "team_size",
        1
    )

    service_name = analysis.get(
        "service"
    )

    db = SessionLocal()

    try:

        service = db.query(Service).filter(
            Service.name == service_name
        ).first()

        if not service:

            return {
                "success": False,
                "message": "Service not found."
            }

        workers = db.query(Worker).filter(
            Worker.service_id == service.id,
            Worker.availability == True
        ).all()

        worker_data = []

        for worker in workers:

            worker_data.append({
                "id": worker.id,
                "name": worker.name,
                "skills": worker.skills,
                "availability": worker.availability,
                "rating": worker.rating,
                "reliability_score": worker.reliability_score,
                "completed_jobs": worker.completed_jobs,
                "latitude": getattr(
                    worker,
                    "latitude",
                    None
                ),
                "longitude": getattr(
                    worker,
                    "longitude",
                    None
                )
            })

        team = select_team(
            worker_data,
            team_size,
            float(customer_lat),
            float(customer_lon),
            analysis.get("problem"),
            analysis.get("required_components")
        )
        recommendation = generate_team_recommendation(
             team
        )
        service_plan = create_service_plan(
            analysis,
            team,
           recommendation
        )
        booking_data = create_complex_booking_data(
            analysis,
            team,
            recommendation
        )
        return {
    "success": True,
    "analysis": analysis,
    "team_matching": team,
    "recommendation": recommendation,
    "service_plan": service_plan,
    "booking_data": booking_data
}
    finally:

        db.close()
def create_complex_booking_data(
    analysis,
    team_matching,
    recommendation
):

    return {
        "service": analysis.get(
            "service"
        ),
        "problem": analysis.get(
            "problem"
        ),
        "property_type": analysis.get(
            "property_type"
        ),
        "origin": analysis.get(
            "origin"
        ),
        "destination": analysis.get(
            "destination"
        ),
        "team_size_required": analysis.get(
            "team_size",
            1
        ),
        "workers_selected": team_matching.get(
            "team_size_selected",
            0
        ),
        "workers_shortage": recommendation.get(
            "shortage",
            0
        ),
        "vehicle_required": analysis.get(
            "vehicle_required",
            False
        ),
        "resources": analysis.get(
            "resources",
            []
        ),
        "booking_status": (
            "Awaiting Team"
            if not team_matching.get(
                "team_complete",
                False
            )
            else "Ready for Booking"
        )
    }
@app.post("/ai/prepare-booking")
def prepare_complex_booking(request: dict):

    request_text = request.get(
        "request",
        ""
    ).strip()

    customer_lat = request.get(
        "customer_lat",
        13.6288
    )

    customer_lon = request.get(
        "customer_lon",
        79.4192
    )

    if not request_text:

        return {
            "success": False,
            "message": "Request cannot be empty."
        }

    analysis = analyze_request(
        request_text
    )

    if analysis.get(
        "request_type"
    ) != "complex_service":

        return {
            "success": False,
            "message": (
                "This request does not require "
                "complex-service booking."
            )
        }

    team_size = analysis.get(
        "team_size",
        1
    )

    service_name = analysis.get(
        "service"
    )

    db = SessionLocal()

    try:

        service = db.query(Service).filter(
            Service.name == service_name
        ).first()

        if not service:

            return {
                "success": False,
                "message": "Service not found."
            }

        workers = db.query(Worker).filter(
            Worker.service_id == service.id,
            Worker.availability == True
        ).all()

        worker_data = []

        for worker in workers:

            worker_data.append({
                "id": worker.id,
                "name": worker.name,
                "skills": worker.skills,
                "availability": worker.availability,
                "rating": worker.rating,
                "reliability_score":
                    worker.reliability_score,
                "completed_jobs":
                    worker.completed_jobs,
                "latitude":
                    getattr(
                        worker,
                        "latitude",
                        None
                    ),
                "longitude":
                    getattr(
                        worker,
                        "longitude",
                        None
                    )
            })

        team = select_team(
            worker_data,
            team_size,
            float(customer_lat),
            float(customer_lon),
            analysis.get("problem"),
            analysis.get(
                "required_components"
            )
        )

        recommendation = generate_team_recommendation(
            team
        )

        service_plan = create_service_plan(
            analysis,
            team,
            recommendation
        )

        booking_data = create_complex_booking_data(
            analysis,
            team,
            recommendation
        )

        return {
            "success": True,
            "service_plan": service_plan,
            "booking_data": booking_data
        }

    finally:

        db.close()
@app.post("/ai/create-complex-booking")
def create_complex_booking(request: dict):

    customer_id = request.get("customer_id")
    request_text = request.get("request", "").strip()
    scheduled_time = request.get("scheduled_time")
    estimated_price = request.get("estimated_price")
    location = request.get("location")

    customer_lat = request.get(
        "customer_lat",
        13.6288
    )

    customer_lon = request.get(
        "customer_lon",
        79.4192
    )

    if not customer_id:
        return {
            "success": False,
            "message": "Customer ID is required."
        }

    if not request_text:
        return {
            "success": False,
            "message": "Service request is required."
        }

    if not scheduled_time:
        return {
            "success": False,
            "message": "Scheduled time is required."
        }

    if estimated_price is None:
        return {
            "success": False,
            "message": "Estimated price is required."
        }

    db = SessionLocal()

    try:

        # Find customer
        customer = db.query(User).filter(
            User.id == customer_id
        ).first()

        if not customer:
            return {
                "success": False,
                "message": "Customer not found."
            }

        # Analyze request
        analysis = analyze_request(
            request_text
        )

        if analysis.get(
            "request_type"
        ) != "complex_service":

            return {
                "success": False,
                "message": (
                    "This request does not "
                    "require complex-service booking."
                )
            }

        service_name = analysis.get(
            "service"
        )

        team_size = analysis.get(
            "team_size",
            1
        )

        # Find service
        service = db.query(Service).filter(
            Service.name == service_name
        ).first()

        if not service:
            return {
                "success": False,
                "message": "Service not found."
            }

        # Find available workers
        workers = db.query(Worker).filter(
            Worker.service_id == service.id,
            Worker.availability == True
        ).all()

        worker_data = []

        for worker in workers:

            worker_data.append({
                "id": worker.id,
                "name": worker.name,
                "skills": worker.skills,
                "availability": worker.availability,
                "rating": worker.rating,
                "reliability_score":
                    worker.reliability_score,
                "completed_jobs":
                    worker.completed_jobs,
                "latitude":
                    getattr(
                        worker,
                        "latitude",
                        None
                    ),
                "longitude":
                    getattr(
                        worker,
                        "longitude",
                        None
                    )
            })

        # Match team
        team = select_team(
            worker_data,
            team_size,
            float(customer_lat),
            float(customer_lon),
            analysis.get("problem"),
            analysis.get(
                "required_components"
            )
        )

        # Generate recommendation
        recommendation = generate_team_recommendation(
            team
        )

        selected_workers = team.get(
    "team_members",
    []
)

        if not selected_workers:

            return {
                "success": False,
                "message": (
                    "No available worker "
                    "was found for this service."
                )
            }

        # First selected worker becomes lead worker
        lead_worker_id = selected_workers[0].get(
    "worker_id"
)

        lead_worker = db.query(Worker).filter(
            Worker.id == lead_worker_id
        ).first()

        if not lead_worker:

            return {
                "success": False,
                "message": "Lead worker not found."
            }

        # Complex booking status
        booking_status = (
            "requested"
            if team.get("team_complete", False)
            else "awaiting_team"
        )

        # Use origin as location when location
        # is not explicitly provided
        booking_location = location

        if not booking_location:
            booking_location = analysis.get(
                "origin"
            )

        if not booking_location:
            booking_location = customer.location

        # Create main booking
        booking = Booking(
            customer_id=customer_id,
            worker_id=lead_worker_id,
            service_id=service.id,
            status=booking_status,
            location=booking_location,
            scheduled_time=scheduled_time,
            estimated_price=float(
                estimated_price
            )
        )

        db.add(booking)
        db.flush()

        # Attach every selected worker
        for selected_worker in selected_workers:

            booking_worker = BookingWorker(
                booking_id=booking.id,
                worker_id=selected_worker.get(
                   "worker_id"
                ),
                role=(
                    "lead"
                   if selected_worker.get(
                       "worker_id"
                    ) == lead_worker_id
                    else "team_member"
                )
            )

            db.add(booking_worker)

        db.commit()
        db.refresh(booking)

        return {
            "success": True,
            "message": (
                "Complex booking created successfully."
            ),
            "booking": {
                "id": booking.id,
                "customer_id":
                    booking.customer_id,
                "service":
                    service.name,
                "status":
                    booking.status,
                "location":
                    booking.location,
                "scheduled_time":
                    booking.scheduled_time,
                "estimated_price":
                    booking.estimated_price,
                "lead_worker": {
                    "id":
                        lead_worker.id,
                    "name":
                        lead_worker.name
                },
                "team": {
                    "required":
                        team.get(
                            "team_size_requested"
                        ),
                    "selected":
                        team.get(
                            "team_size_selected"
                        ),
                    "complete":
                        team.get(
                            "team_complete"
                        ),
                    "shortage":
                        recommendation.get(
                            "shortage"
                        )
                }
            }
        }

    except Exception as e:

        db.rollback()

        return {
            "success": False,
            "message": (
                "Failed to create complex booking."
            ),
            "error": str(e)
        }

    finally:

        db.close()
# =========================================================
# ASSIGN WORKER TO COMPLEX BOOKING
# =========================================================

@app.post("/ai/assign-team-worker")
def assign_team_worker(request: dict):

    booking_id = request.get("booking_id")
    worker_id = request.get("worker_id")
    role = request.get("role", "member")

    if not booking_id:
        return {
            "success": False,
            "message": "Booking ID is required."
        }

    if not worker_id:
        return {
            "success": False,
            "message": "Worker ID is required."
        }

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # FIND BOOKING
        # -------------------------------------------------

        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }


        # -------------------------------------------------
        # FIND WORKER
        # -------------------------------------------------

        worker = db.query(Worker).filter(
            Worker.id == worker_id
        ).first()

        if not worker:
            return {
                "success": False,
                "message": "Worker not found."
            }


        # -------------------------------------------------
        # CHECK WORKER AVAILABILITY
        # -------------------------------------------------

        if worker.availability is not True:
            return {
                "success": False,
                "message": "Worker is currently unavailable."
            }


        # -------------------------------------------------
        # FIND BOOKING SERVICE
        # -------------------------------------------------

        service = db.query(Service).filter(
            Service.id == booking.service_id
        ).first()

        if not service:
            return {
                "success": False,
                "message": "Booking service not found."
            }


        # -------------------------------------------------
        # CHECK WORKER SERVICE
        # -------------------------------------------------

        worker_service = db.query(Service).filter(
            Service.id == worker.service_id
        ).first()

        if (
            worker_service
            and worker_service.name != service.name
        ):
            return {
                "success": False,
                "message": (
                    f"Worker is registered for "
                    f"{worker_service.name}, not "
                    f"{service.name}."
                )
            }


        # -------------------------------------------------
        # CHECK DUPLICATE ASSIGNMENT
        # -------------------------------------------------

        existing_assignment = db.query(
            BookingWorker
        ).filter(
            BookingWorker.booking_id == booking_id,
            BookingWorker.worker_id == worker_id
        ).first()

        if existing_assignment:
            return {
                "success": False,
                "message": (
                    "Worker is already assigned "
                    "to this booking."
                )
            }


        # -------------------------------------------------
        # CREATE TEAM ASSIGNMENT
        # -------------------------------------------------

        assignment = BookingWorker(
            booking_id=booking_id,
            worker_id=worker_id,
            role=role
        )

        db.add(assignment)
        db.commit()
        db.refresh(assignment)


        # -------------------------------------------------
        # COUNT ASSIGNED WORKERS
        # -------------------------------------------------

        assigned_workers = db.query(
            BookingWorker
        ).filter(
            BookingWorker.booking_id == booking_id
        ).all()

        assigned_count = len(assigned_workers)


        # -------------------------------------------------
        # REQUIRED TEAM SIZE
        # -------------------------------------------------

        if service.name == "Packers & Movers":
            required_team_size = 3
        else:
            required_team_size = 1


        # -------------------------------------------------
        # UPDATE BOOKING STATUS
        # -------------------------------------------------

        if assigned_count >= required_team_size:

            booking.status = "requested"

            db.commit()

            remaining = 0

            status_message = (
                "Required team is complete. "
                "Booking is now requested."
            )

        else:

            booking.status = "awaiting_team"

            db.commit()

            remaining = (
                required_team_size
                - assigned_count
            )

            status_message = (
                "Worker assigned successfully. "
                f"{remaining} additional worker(s) "
                "still required."
            )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {
            "success": True,
            "message": status_message,

            "assignment": {
                "id": assignment.id,
                "booking_id": assignment.booking_id,
                "worker_id": assignment.worker_id,
                "worker_name": worker.name,
                "role": assignment.role
            },

            "team": {
                "required": required_team_size,
                "assigned": assigned_count,
                "remaining": remaining,
                "complete": (
                    assigned_count >= required_team_size
                )
            },

            "booking": {
                "id": booking.id,
                "status": booking.status
            }
        }

    finally:
        db.close()