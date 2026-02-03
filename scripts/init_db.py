"""Initialize database tables."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import Base, engine
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.slot import Slot
from src.models.booking import Booking
from src.models.questionnaire import ComplianceQuestionnaire, TriageQuestionnaire


async def init_db():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
