import logging
import random

from faker import Faker
from werkzeug.security import generate_password_hash

from src.auth.models import VNRole, VNUser
from src.exts import db
from src.tenant.models import VNHouse, VNHouseOwner, VNTenant

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker(["fr_FR"])


class SeedManager:
    def __init__(self, count=5):
        self.count = count

    def run(self):
        logger.info(f"Seeding {self.count} items for each major model...")

        # 1. Ensure Roles exist
        VNRole.insert_roles()

        # 2. Create Agencies (Users with company flag)
        agencies = []
        staff_role = VNRole.query.filter_by(role_name="Staff").first()
        if not staff_role:
            logger.error("Staff role not found! Please run init-db first.")
            return

        for _ in range(self.count):
            email = fake.unique.email()
            user = VNUser(
                vn_addr_email=email,
                vn_fullname=fake.company(),
                vn_password=generate_password_hash("password123"),
                vn_phonenumber_one=fake.phone_number(),
                vn_company=True,
                vn_activated=True,
            )
            user.vn_role_id = staff_role.id  # Assign using actual database ID
            db.session.add(user)
            agencies.append(user)

        db.session.commit()
        logger.info(f"Created {len(agencies)} Agencies.")

        # 3. Create Owners for each Agency
        owners = []
        for agency in agencies:
            for _ in range(random.randint(1, 3)):
                owner = VNHouseOwner(
                    vn_fullname=fake.name(),
                    vn_phonenumber_one=fake.phone_number(),
                    vn_addr_email=fake.unique.email(),
                    vn_user_id=agency.id,
                    vn_owner_percent=random.choice([5.0, 10.0, 15.0]),
                )
                db.session.add(owner)
                owners.append(owner)

        db.session.commit()
        logger.info(f"Created {len(owners)} Owners.")

        # 4. Create Houses for each Owner
        houses = []
        house_types = ["Studio", "Appartement", "Villa", "Bureau"]
        for owner in owners:
            for _ in range(random.randint(1, 2)):
                house = VNHouse(
                    vn_house_type=random.choice(house_types),
                    vn_house_rent=float(random.randint(50000, 500000)),
                    vn_house_guaranty=float(random.randint(50000, 100000)),
                    vn_house_address=fake.address(),
                    vn_owner_id=owner.id,
                    vn_user_id=owner.vn_user_id,
                    vn_house_is_open=True,
                )
                db.session.add(house)
                houses.append(house)

        db.session.commit()
        logger.info(f"Created {len(houses)} Houses.")

        # 5. Create Tenants for some Houses
        tenants_count = 0
        for house in houses:
            if random.random() > 0.3:  # 70% chance of being rented
                tenant = VNTenant(
                    vn_fullname=fake.name(),
                    vn_phonenumber_one=fake.phone_number(),
                    vn_addr_email=fake.unique.email(),
                    vn_house_id=house.id,
                    vn_owner_id=house.vn_owner_id,
                    vn_user_id=house.vn_user_id,
                )
                house.vn_house_is_open = False  # Mark as rented
                db.session.add(tenant)
                tenants_count += 1

        db.session.commit()
        logger.info(f"Created {tenants_count} Tenants.")
        logger.info("Seeding complete!")
