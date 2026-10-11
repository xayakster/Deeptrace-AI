"""
DeepTrace AI - Server Entry Point.
Delegates to backend.app for application routes, state, and execution.
"""

import os
import sys

# Ensure workspace root and backend directory are in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

for path in [PROJECT_ROOT, BACKEND_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.app import (
    app,
    allowed_file,
    UPLOAD_FOLDER,
    ANALYSIS_RECORD_CACHE,
    AnalysisRecordCache,
    ForensicReport,
    main,
)

if __name__ == "__main__":
    main()