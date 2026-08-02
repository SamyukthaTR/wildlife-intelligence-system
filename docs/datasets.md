# Wildlife Datasets Ingestion Architecture

The Wildlife Intelligence System supports importing historical and ongoing datasets from major public biodiversity repositories. Because each repository uses different APIs, data structures, and media formats, we use an **Abstract Adapter Pattern** to standardize ingestion into the core `ObservationLog` pipeline.

## The `DatasetAdapter` Interface

All dataset parsers must implement the `DatasetAdapter` Abstract Base Class (defined in `backend/scripts/seed_dataset.py`).

```python
class DatasetAdapter(ABC):
    @abstractmethod
    def fetch_metadata(self) -> List[Dict]:
        """
        Returns a standardized list of dictionaries containing:
        - source_id: Unique identifier from external system
        - local_file_path: Where the file is locally cached or bundled
        - file_type: 'image' or 'audio'
        - timestamp: Capture datetime
        """
        pass
```

The unified ingestion script (`seed_dataset.py`) calls `fetch_metadata()`, verifies idempotency (ensuring we don't duplicate `source_id`s in the `observation_log`), and persists the media into local storage, wiring it up to a System User (`seed_system@wildlife.org`), Site, Survey, and Device.

## Extending for Global Datasets

Future implementations will subclass `DatasetAdapter` to parse the following datasets:

### 1. iNaturalist
- **Adapter Strategy**: `iNaturalistAdapter` will hit the iNaturalist REST API (`/v1/observations`) filtering for "research-grade" observations within specific bounding boxes. 
- **Media**: Download `observation_photos` sequentially to a staging folder, emitting the iNaturalist Observation ID as the `source_id`.

### 2. BirdCLEF
- **Adapter Strategy**: `BirdClefAdapter` will process bulk local archives (typically downloaded from Kaggle). 
- **Media**: It will parse the accompanying `train_metadata.csv` to map audio chunks (`.ogg` or `.wav`) to specific survey sites and emit 'audio' types, mapping the `filename` as the `source_id`.

### 3. Animal Kingdom (AK) Dataset
- **Adapter Strategy**: `AnimalKingdomAdapter` will map action-recognition video sequences and image sequences.
- **Media**: Parses the `annotation.json` COCO-style files to extract the frames/video paths.

### 4. GBIF (Global Biodiversity Information Facility)
- **Adapter Strategy**: `GbifAdapter` will read Darwin Core (DwC) Archives. 
- **Media**: It will join the `occurrence.txt` file with the `multimedia.txt` extension, downloading the media URLs and mapping the GBIF `occurrenceID` to the `source_id`.

---

## Current Implementations

### Snapshot Serengeti
We provide a local-first `SnapshotSerengetiAdapter` that seeds the database with a small bundle of genuine Snapshot Serengeti images derived from the live LILA BC Azure Blob.
**Attribution & License**: Released under the [Creative Commons Attribution 4.0 International License (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/) or public domain equivalent. Originally published via LILA BC and Zooniverse.

### BirdCLEF
We provide a `BirdClefAdapter` that seeds genuine audio files sourced directly from Xeno-canto contributors. 
**Attribution & License**: Audio recordings are provided by individual contributors to Xeno-canto. Specific licenses vary by recording (frequently CC-BY-NC-SA or CC-BY-NC).

### iNaturalist
We provide an `INaturalistAdapter` that pulls genuine research-grade observations.
**Attribution & License**: Data provided by the iNaturalist community. The specific sample data fetched in this seed bundle is licensed under **CC-BY-NC** by the original photographer.

### GBIF
We provide a `GbifAdapter` pulling genuine occurrence records.
**Attribution & License**: Provided by GBIF publishers under CC0, CC-BY, or CC-BY-NC.

### Animal Kingdom (DEFERRED)
**Note**: The `AnimalKingdomAdapter` is currently **deferred**. The Animal Kingdom dataset requires downloading multi-gigabyte zip files hosted on Google Drive, which introduces authentication limits and manual extraction steps that are impractical for a lightweight automated sample seed script. It will be implemented in later stages.
