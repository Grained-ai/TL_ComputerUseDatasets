# TL_ComputerUseDatasets

TL_ComputerUseDatasets is a modular pipeline we developed for TML to support computer usage data processing. It covers data acquisition, cleaning, and query generation, enabling efficient analysis and modeling of user behavior across devices.

## 🏗️ Project Architecture

### Overview
This project follows a modular architecture designed for scalability and maintainability. Each platform (Bilibili, YouTube, etc.) is implemented as a separate module with standardized interfaces for data acquisition and processing.

### Core Components

```
TL_ComputerUseDatasets/
├── .gitignore             # Git ignore rules
├── .idea/                 # IDE configuration files
├── README.md              # Project documentation
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── modules/               # Platform-specific modules
│   ├── __init__.py
│   └── bilibili/         # Bilibili platform module
│       ├── __init__.py
│       ├── list_fetcher.py   # Video list acquisition
│       └── video_fetcher.py  # Individual video data fetching
├── scripts/              # Utility scripts and tools
│   └── __init__.py
├── data/                 # Sample data and datasets
│   └── README.md

```

### Architecture Principles

1. **Modular Design**: Each platform is encapsulated in its own module
2. **Standardized Interfaces**: Common APIs across all platform modules
3. **Separation of Concerns**: Clear distinction between data acquisition, processing, and storage
4. **Type Safety**: Full TypeScript-style type annotations for Python code
5. **Extensibility**: Easy to add new platforms and data sources

### Data Flow

```
Platform APIs → Module Fetchers → Data Models → Processing Pipeline → Output
```

1. **Data Acquisition**: Platform-specific fetchers retrieve raw data
2. **Data Modeling**: Raw data is transformed into standardized models
3. **Processing**: Data cleaning, validation, and enrichment
4. **Output**: Structured datasets ready for analysis

### Module Structure

Each platform module follows this standard structure:

- **`list_fetcher.py`**: Handles bulk data acquisition (video lists, playlists, etc.)
- **`video_fetcher.py`**: Handles individual item data fetching with detailed metadata
- **`__init__.py`**: Module initialization and exports

### Current Implementation Status

#### ✅ Completed Components
- **Project Structure**: Basic directory structure established
- **Bilibili Module**: Core fetcher classes implemented
  - `BilibiliListFetcher`: Video list acquisition functionality
  - `BilibiliVideoFetcher`: Individual video data fetching


#### 🚧 Planned Components
- **Data Models**: Pydantic models for data validation and serialization
- **Utility Functions**: Platform-specific utility functions and helpers
- **Configuration System**: YAML-based configuration management
- **Validation Rules**: Data quality validation and processing rules

### Technology Stack

- **Backend**: FastAPI for API endpoints
- **Data Processing**: Python with Pydantic for data validation
- **Database**: PostgreSQL for structured data storage
- **Type Safety**: Full type annotations throughout the codebase

## 🚀 Getting Started

### Installation

```bash
pip install -r requirements.txt
```

## 📁 Module Documentation

### Bilibili Module

The Bilibili module provides data acquisition capabilities for the Bilibili platform.

#### Current Features
- Modular structure with separate fetcher classes
- Async/await support for concurrent operations
- Basic error handling framework

#### Components
- **`BilibiliListFetcher`**: Bulk video list acquisition (implementation in progress)
- **`BilibiliVideoFetcher`**: Detailed video data extraction (implementation in progress)
- **Module Exports**: Centralized imports through `__init__.py`

#### Usage Example
```python
from modules.bilibili import BilibiliListFetcher, BilibiliVideoFetcher

# Initialize fetchers
list_fetcher = BilibiliListFetcher()
video_fetcher = BilibiliVideoFetcher()

# Fetch user videos (when implemented)
# videos = await list_fetcher.fetch_user_videos(user_id="123456")
```

## 🔧 Development

### Development Roadmap

#### Phase 1: Core Infrastructure ✅
- [x] Project structure setup
- [x] Basic module framework
- [x] Documentation foundation
- [x] Dependency management

#### Phase 2: Bilibili Module Implementation 🚧
- [ ] API client with rate limiting
- [ ] List fetcher implementation
- [ ] Video fetcher implementation
- [ ] Error handling and logging
- [ ] Unit tests


### Adding New Platforms

1. Create a new module directory under `modules/`
2. Implement the standard fetcher interfaces
3. Define platform-specific data models
4. Add configuration and utility functions

### Code Standards

- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Write unit tests for all public methods

