import os
import shutil
import datetime
import json
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
    """
    @abstractmethod
    def fetch_metadata(self) -> List[Dict]:
        pass

class SnapshotSerengetiAdapter(DatasetAdapter):
    def __init__(self, sample_dir: str):
        self.sample_dir = sample_dir

    def fetch_metadata(self) -> List[Dict]:
        metadata = []
        if not os.path.exists(self.sample_dir): return metadata
        for filename in os.listdir(self.sample_dir):
            if filename.startswith("S1_B06"):
                metadata.append({
                    "source_id": f"snapshot_serengeti_{filename}",
                    "local_file_path": os.path.join(self.sample_dir, filename),
                    "file_type": "image",
                    "timestamp": datetime.datetime.now()
                })
        return metadata

class BirdClefAdapter(DatasetAdapter):
    def __init__(self, sample_dir: str):
        self.sample_dir = sample_dir

    def fetch_metadata(self) -> List[Dict]:
        metadata = []
        if not os.path.exists(self.sample_dir): return metadata
        for filename in os.listdir(self.sample_dir):
            if filename.endswith(".mp3"):
                metadata.append({
                    "source_id": f"birdclef_{filename}",
                    "local_file_path": os.path.join(self.sample_dir, filename),
                    "file_type": "audio",
                    "timestamp": datetime.datetime.now()
                })
        return metadata

class INaturalistAdapter(DatasetAdapter):
    def __init__(self, sample_dir: str):
        self.sample_dir = sample_dir

    def fetch_metadata(self) -> List[Dict]:
        metadata = []
        if not os.path.exists(self.sample_dir): return metadata
        # We also stored a metadata.json
        for filename in os.listdir(self.sample_dir):
            if filename.endswith(".jpg"):
                metadata.append({
                    "source_id": f"inaturalist_{filename}",
                    "local_file_path": os.path.join(self.sample_dir, filename),
                    "file_type": "image",
                    "timestamp": datetime.datetime.now()
                })
        return metadata

class GbifAdapter(DatasetAdapter):
    def __init__(self, sample_dir: str):
        self.sample_dir = sample_dir

    def fetch_metadata(self) -> List[Dict]:
        metadata = []
        if not os.path.exists(self.sample_dir): return metadata
        for filename in os.listdir(self.sample_dir):
            if filename.endswith(".jpg"):
                metadata.append({
                    "source_id": f"gbif_{filename}",
                    "local_file_path": os.path.join(self.sample_dir, filename),
                    "file_type": "image",
                    "timestamp": datetime.datetime.now()
                })
        return metadata


def get_or_create_seed_user(db) -> User:
    email = "seed_system@wildlife.org"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            name="System Seed Process",
            email=email,
            hashed_password=get_password_hash("secureseed123!"),
            role=RoleEnum.RESEARCHER,
            organization="Dataset Ingestion"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_or_create_infrastructure(db, user_id: int, site_name: str, device_serial: str, notes: str):
    site = db.query(MonitoringSite).filter(MonitoringSite.location_name == site_name).first()
    if not site:
        wkt_geom = f"SRID=4326;POINT(0 0)"
        site = MonitoringSite(
            location_name=site_name, geom=wkt_geom, habitat_type="Global",
            protected_area="Various", monitoring_device_type="mixed", created_by=user_id
        )
        db.add(site)
        db.commit()
        db.refresh(site)

    survey = db.query(Survey).filter(Survey.site_id == site.id).first()
    if not survey:
        survey = Survey(
            site_id=site.id, survey_date=datetime.date.today(),
            status=SurveyStatusEnum.COMPLETED, notes=notes
        )
        db.add(survey)
        db.commit()
        db.refresh(survey)

    device = db.query(Device).filter(Device.serial == device_serial).first()
    if not device:
        device = Device(site_id=site.id, device_type=DeviceTypeEnum.CAMERA_TRAP, serial=device_serial, status="active")
        db.add(device)
        db.commit()

    return site, survey, device


def seed_database():
    db = SessionLocal()
    try:
        seed_user = get_or_create_seed_user(db)
        uploads_dir = "/app/uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        adapters = [
            (SnapshotSerengetiAdapter("/app/scripts/sample_data/snapshot_serengeti"), "Serengeti NP - Grid S1", "SS-CAM-S1-01", "Snapshot Serengeti Seed"),
            (BirdClefAdapter("/app/scripts/sample_data/birdclef"), "BirdCLEF Xeno-Canto Region", "BC-MIC-01", "BirdCLEF Seed"),
            (INaturalistAdapter("/app/scripts/sample_data/inaturalist"), "iNaturalist Global", "INAT-USER-01", "iNat Seed"),
            (GbifAdapter("/app/scripts/sample_data/gbif"), "GBIF Global", "GBIF-01", "GBIF Seed")
        ]

        total_inserts = 0
        for adapter, site_name, dev_serial, notes in adapters:
            print(f"\\nRunning {adapter.__class__.__name__}...")
            site, survey, device = get_or_create_infrastructure(db, seed_user.id, site_name, dev_serial, notes)
            records = adapter.fetch_metadata()

            if not records:
                print(f"  [WARN] No sample data found for {adapter.__class__.__name__}.")
                continue

            for record in records:
                source_id = record["source_id"]
                existing = db.query(ObservationLog).filter(
                    ObservationLog.storage_path.like(f"%{source_id}")
                ).first()

                if existing:
                    print(f"  [SKIP] Record {source_id} already ingested.")
                    continue

                final_path = os.path.join(uploads_dir, source_id)
                shutil.copy(record["local_file_path"], final_path)

                obs = ObservationLog(
                    survey_id=survey.id,
                    uploaded_by=seed_user.id,
                    file_type=FileTypeEnum.IMAGE if record["file_type"] == 'image' else FileTypeEnum.AUDIO,
                    storage_path=final_path,
                    uploaded_at=record["timestamp"],
                    processing_status="pending"
                )
                db.add(obs)
                total_inserts += 1
                print(f"  [INSERT] Seeded {source_id}")
            db.commit()
            
        print(f"\\nDataset seed complete. Added {total_inserts} total new observations.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
