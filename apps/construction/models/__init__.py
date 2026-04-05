"""
Construction models - Simple Mode (default) + Advanced Mode (CPM/EVM).

Organização:
- phase.py: ConstructionPhase (WBS Level 1)
- task.py: ConstructionTask (core - Simple Mode default)
- progress.py: TaskPhoto (progress tracking)
- cpm.py: TaskDependency, CPMSnapshot (Advanced Mode)
- evm.py: EVMSnapshot (Advanced Mode)
"""

from .phase import ConstructionPhase
from .task import ConstructionTask
from .progress import TaskPhoto, TaskProgressLog
from .cpm import TaskDependency, CPMSnapshot
from .evm import EVMSnapshot

__all__ = [
    'ConstructionPhase',
    'ConstructionTask',
    'TaskPhoto',
    'TaskProgressLog',
    'TaskDependency',
    'CPMSnapshot',
    'EVMSnapshot',
]
