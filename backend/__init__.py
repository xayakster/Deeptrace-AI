"""
DeepTrace AI - Backend Package
Provides Flask API application and modular digital forensics engine.
"""

from backend.app import (
    app,
    allowed_file,
    UPLOAD_FOLDER,
    ANALYSIS_RECORD_CACHE,
    AnalysisRecordCache,
    main,
)

__all__ = [
    "app",
    "allowed_file",
    "UPLOAD_FOLDER",
    "ANALYSIS_RECORD_CACHE",
    "AnalysisRecordCache",
    "main",
]
