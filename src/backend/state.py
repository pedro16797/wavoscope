from typing import Optional
from session.project import Project

project: Optional[Project] = None

# Export state
export_active: bool = False
export_progress: float = 0.0
export_message: str = ""
