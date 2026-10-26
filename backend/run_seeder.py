import asyncio
import shutil
import sys
from app.core.database import AsyncSessionLocal, init_db
from app.services.seeder import seed_sample_data

async def main():
    print("Initializing DB...")
    await init_db()
    async with AsyncSessionLocal() as session:
        print("Seeding sample data...")
        res = await seed_sample_data(session, force_reset=True)
        print("Done seeding:", res["message"])
    shutil.copyfile("tender_assistant.db", "../tender_assistant.db")
    print("Database synced to root.")

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
