
from .database import Base, engine, SessionLocal
from .models import User, Service, Worker


def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. CREATE MISSING SERVICES
        # ---------------------------------------------------------

        services_data = [
            {
                "name": "Plumbing",
                "category": "Home Repair",
                "base_price": 500
            },
            {
                "name": "Electrical",
                "category": "Home Repair",
                "base_price": 400
            },
            {
                "name": "Cleaning",
                "category": "Home Services",
                "base_price": 600
            },
            {
                "name": "Gardening",
                "category": "Outdoor Services",
                "base_price": 500
            },
            {
                "name": "Carpentry",
                "category": "Home Repair",
                "base_price": 700
            },
            {
                "name": "Caretaking",
                "category": "Care Services",
                "base_price": 800
            },
            {
                "name": "Driving",
                "category": "Transport Services",
                "base_price": 700
            },
            {
                "name": "Packers & Movers",
                "category": "Moving Services",
                "base_price": 2500
            }
        ]

        for data in services_data:
            existing_service = db.query(Service).filter(
                Service.name == data["name"]
            ).first()

            if not existing_service:
                service = Service(
                    name=data["name"],
                    category=data["category"],
                    base_price=data["base_price"]
                )

                db.add(service)
                print(f"Created service: {data['name']}")

        db.commit()

        # Get all services after creation
        services = db.query(Service).all()

        service_map = {
            service.name: service.id
            for service in services
        }

        # ---------------------------------------------------------
        # 2. WORKER DATA
        # ---------------------------------------------------------

        workers_data = [

            # -------------------------
            # EXISTING WORKERS
            # -------------------------

            {
                "name": "Ravi Kumar",
                "phone": "9000000001",
                "service": "Plumbing",
                "skills": "Pipe Repair,Leakage Repair,Tap Installation",
                "location": "Tirupati",
                "latitude": 13.6288,
                "longitude": 79.4192,
                "rating": 4.8,
                "completed_jobs": 124,
                "reliability_score": 94
            },

            {
                "name": "Suresh Reddy",
                "phone": "9000000002",
                "service": "Plumbing",
                "skills": "Pipe Repair,Water Tank,Leakage Repair",
                "location": "Tirupati",
                "latitude": 13.6350,
                "longitude": 79.4100,
                "rating": 4.6,
                "completed_jobs": 98,
                "reliability_score": 91
            },

            {
                "name": "Arjun Kumar",
                "phone": "9000000003",
                "service": "Electrical",
                "skills": "Wiring,Fan Repair,Switch Repair",
                "location": "Tirupati",
                "latitude": 13.6200,
                "longitude": 79.4300,
                "rating": 4.9,
                "completed_jobs": 156,
                "reliability_score": 96
            },

            {
                "name": "Mahesh Babu",
                "phone": "9000000004",
                "service": "Cleaning",
                "skills": "House Cleaning,Deep Cleaning,Bathroom Cleaning",
                "location": "Tirupati",
                "latitude": 13.6250,
                "longitude": 79.4150,
                "rating": 4.7,
                "completed_jobs": 87,
                "reliability_score": 89
            },

            {
                "name": "Anil Kumar",
                "phone": "9000000005",
                "service": "Gardening",
                "skills": "Lawn Care,Plant Care,Pruning",
                "location": "Tirupati",
                "latitude": 13.6400,
                "longitude": 79.4200,
                "rating": 4.5,
                "completed_jobs": 76,
                "reliability_score": 88
            },

            {
                "name": "Prakash Rao",
                "phone": "9000000006",
                "service": "Carpentry",
                "skills": "Furniture Repair,Wood Work,Door Repair",
                "location": "Tirupati",
                "latitude": 13.6300,
                "longitude": 79.4250,
                "rating": 4.8,
                "completed_jobs": 112,
                "reliability_score": 93
            },

            {
                "name": "Vijay Movers",
                "phone": "9000000007",
                "service": "Packers & Movers",
                "skills": "Packing,Loading,Furniture Handling",
                "location": "Tirupati",
                "latitude": 13.6150,
                "longitude": 79.4050,
                "rating": 4.6,
                "completed_jobs": 64,
                "reliability_score": 90
            },

            # -------------------------
            # NEW CARETAKERS
            # -------------------------

            {
                "name": "Lakshmi Caregiver",
                "phone": "9000000010",
                "service": "Caretaking",
                "skills": "Elderly Care,Patient Care,Home Care",
                "location": "Tirupati",
                "latitude": 13.6240,
                "longitude": 79.4170,
                "rating": 4.8,
                "completed_jobs": 68,
                "reliability_score": 92
            },

            {
                "name": "Anitha Caregiver",
                "phone": "9000000011",
                "service": "Caretaking",
                "skills": "Child Care,Elderly Care,Home Care",
                "location": "Tirupati",
                "latitude": 13.6320,
                "longitude": 79.4140,
                "rating": 4.7,
                "completed_jobs": 54,
                "reliability_score": 90
            },

            # -------------------------
            # NEW DRIVERS
            # -------------------------

            {
                "name": "Ramesh Driver",
                "phone": "9000000012",
                "service": "Driving",
                "skills": "Personal Driver,Car Driving,Local Driving",
                "location": "Tirupati",
                "latitude": 13.6210,
                "longitude": 79.4210,
                "rating": 4.8,
                "completed_jobs": 91,
                "reliability_score": 93
            },

            {
                "name": "Srinivas Driver",
                "phone": "9000000013",
                "service": "Driving",
                "skills": "Vehicle Driving,Scheduled Driving,Outstation Driving",
                "location": "Tirupati",
                "latitude": 13.6160,
                "longitude": 79.4280,
                "rating": 4.6,
                "completed_jobs": 73,
                "reliability_score": 89
            }
        ]

        # ---------------------------------------------------------
        # 3. CREATE ONLY MISSING WORKERS
        # ---------------------------------------------------------

        workers_created = 0

        for data in workers_data:

            # Check phone number so existing workers are not duplicated
            existing_user = db.query(User).filter(
                User.phone == data["phone"]
            ).first()

            if existing_user:
                print(
                    f"Worker already exists: {data['name']}"
                )
                continue

            service_id = service_map.get(data["service"])

            if not service_id:
                print(
                    f"Service not found: {data['service']}"
                )
                continue

            user = User(
                name=data["name"],
                phone=data["phone"],
                role="worker",
                location=data["location"]
            )

            db.add(user)
            db.flush()

            worker = Worker(
                user_id=user.id,
                service_id=service_id,
                name=data["name"],
                skills=data["skills"],
                location=data["location"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                rating=data["rating"],
                completed_jobs=data["completed_jobs"],
                availability=True,
                verification_status="verified",
                reliability_score=data["reliability_score"]
            )

            db.add(worker)
            workers_created += 1

        db.commit()

        # ---------------------------------------------------------
        # 4. FINAL DATABASE SUMMARY
        # ---------------------------------------------------------

        total_services = db.query(Service).count()
        total_workers = db.query(Worker).count()

        print()
        print("==========================================")
        print("SAHAKAR SEVA DATABASE SEED COMPLETE")
        print("==========================================")
        print(f"Total services: {total_services}")
        print(f"Total workers: {total_workers}")
        print(f"New workers created: {workers_created}")
        print()
        print("Service-wise worker count:")

        for service in db.query(Service).order_by(Service.id).all():

            worker_count = db.query(Worker).filter(
                Worker.service_id == service.id
            ).count()

            print(
                f"  {service.name}: "
                f"{worker_count} worker(s)"
            )

        print("==========================================")

    except Exception as e:
        db.rollback()

        print()
        print("Database seeding failed.")
        print(f"Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()