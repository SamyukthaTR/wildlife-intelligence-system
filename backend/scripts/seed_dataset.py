import os
import shutil
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict

# Setup local imports assuming script is run via `python -m scripts.seed_dataset`
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.modules.users.models import User, RoleEnum
from app.modules.monitoring.models import MonitoringSite, Survey, Device, DeviceTypeEnum, SurveyStatusEnum
from app.modules.observations.models import ObservationLog, FileTypeEnum

class DatasetAdapter(ABC):
    """
    Abstract Base Class for ingesting external wildlife datasets.
    Implementations of this class will parse specific formats (iNaturalist APIs, BirdCLEF audio bundles, GBIF DarwinCore)
    and adapt them into the standardized Wildlife Intelligence System DB schema.
    """

    @abstractmethod
    def fetch_metadata(self) -> List[Dict]:
        """
        Retrieves the raw metadata for the dataset.
        Should return a standardized list of dictionaries containing keys:
        - source_id: A unique identifier from the external system (used for idempotency).
        - local_file_path: Where the file is locally cached or bundled.
        - file_type: 'image' or 'audio'
        - timestamp: datetime object of the capture
        """
        pass


class SnapshotSerengetiAdapter(DatasetAdapter):
    """
    Adapter for Snapshot Serengeti.
    Currently uses a localized bundle of sample data to ensure reliable execution 
    without risking network timeouts or external rate limits.
    """
    def __init__(self, sample_dir: str):
        self.sample_dir = sample_dir

    def fetch_metadata(self) -> List[Dict]:
        # In a real implementation, this might read a JSON or CSV manifest downloaded alongside the dataset.
        # Since we bundled 2 images into `sample_data/` explicitly:
        metadata = []
        
        # We explicitly search for our mock files
        if not os.path.exists(self.sample_dir):
            return metadata

        for filename in os.listdir(self.sample_dir):
            if filename.startswith("snapshot_serengeti_") and filename.endswith((".jpg", ".png")):
                source_id = filename  # The filename itself is our unique source ID
                local_path = os.path.join(self.sample_dir, filename)
                metadata.append({
                    "source_id": source_id,
                    "local_file_path": local_path,
                    "file_type": "image",
                    "timestamp": datetime.datetime.now() # Mocking current time for the sample
                })
        return metadata


def get_or_create_seed_user(db) -> User:
    """Ensure the system seed user exists."""
    email = "seed_system@wildlife.org"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"Creating seed system user ({email})...")
        user = User(
            name="System Seed Process",
            email=email,
            hashed_password=get_password_hash("secureseed123!"),
            role=RoleEnum.RESEARCHER,
            organization="Snapshot Serengeti Project"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_or_create_infrastructure(db, user_id: int):
    """Ensure the Site, Survey, and Device exist for Snapshot Serengeti."""
    site_name = "Serengeti NP - Grid S1"
    
    # 1. Site
    site = db.query(MonitoringSite).filter(MonitoringSite.location_name == site_name).first()
    if not site:
        print(f"Creating Monitoring Site: {site_name}...")
        wkt_geom = f"SRID=4326;POINT(34.8333 -2.3333)" # Approx Serengeti coordinates
        site = MonitoringSite(
            location_name=site_name,
            geom=wkt_geom,
            habitat_type="Savanna",
            protected_area="Serengeti National Park",
            monitoring_device_type="camera_trap",
            created_by=user_id
        )
        db.add(site)
        db.commit()
        db.refresh(site)

    # 2. Survey
    survey = db.query(Survey).filter(Survey.site_id == site.id).first()
    if not survey:
        print("Creating Survey...")
        survey = Survey(
            site_id=site.id,
            survey_date=datetime.date.today(),
            status=SurveyStatusEnum.COMPLETED,
            notes="Snapshot Serengeti - Season 1 Seed Data"
        )
        db.add(survey)
        db.commit()
        db.refresh(survey)

    # 3. Device
    device_serial = "SS-CAM-S1-01"
    device = db.query(Device).filter(Device.serial == device_serial).first()
    if not device:
        print("Creating Device...")
        device = Device(
            site_id=site.id,
            device_type=DeviceTypeEnum.CAMERA_TRAP,
            serial=device_serial,
            status="active"
        )
        db.add(device)
        db.commit()

    return site, survey, device


def seed_database():
    db = SessionLocal()
    try:
        # 1. Setup ownership
        seed_user = get_or_create_seed_user(db)
        
        # 2. Setup infrastructure hierarchy
        site, survey, device = get_or_create_infrastructure(db, seed_user.id)

        # 3. Initialize Adapter
        sample_dir = "/app/scripts/sample_data"
        uploads_dir = "/app/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        adapter = SnapshotSerengetiAdapter(sample_dir)
        records = adapter.fetch_metadata()

        if not records:
            print(f"No bundle found in {sample_dir}. Exiting.")
            return

        # 4. Idempotent Ingestion
        print(f"Processing {len(records)} records from Snapshot Serengeti...")
        new_inserts = 0
        
        for record in records:
            source_id = record["source_id"]
            
            # Idempotency check: Look for an observation whose storage_path ends with our source_id
            existing = db.query(ObservationLog).filter(
                ObservationLog.storage_path.like(f"%{source_id}")
            ).first()

            if existing:
                print(f"  [SKIP] Record {source_id} already ingested.")
                continue

            # Move file to permanent storage
            final_path = os.path.join(uploads_dir, source_id)
            shutil.copy(record["local_file_path"], final_path)

            # Insert DB Row
            obs = ObservationLog(
                survey_id=survey.id,
                uploaded_by=seed_user.id,
                file_type=FileTypeEnum.IMAGE if record["file_type"] == 'image' else FileTypeEnum.AUDIO,
                storage_path=final_path,
                uploaded_at=record["timestamp"],
                processing_status="pending"
            )
            db.add(obs)
            new_inserts += 1
            print(f"  [INSERT] Seeded {source_id}")

        db.commit()
        print(f"Dataset seed complete. Added {new_inserts} new observations.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
