
from app.database import SessionLocal
from app.services.completed_hackathon_updater import (
    update_completed_hackathons,
)


def main():
    db = SessionLocal()

    try:
        print("Starting weekly HackMates refresh...", flush=True)

        result = update_completed_hackathons(db)

        print("\nWeekly refresh completed.", flush=True)
        print(f"New records: {result['added']}", flush=True)
        print(f"Refreshed records: {result['updated']}", flush=True)
        print(
            f"Total processed: {result['total_processed']}",
            flush=True,
        )

    except Exception as error:
        db.rollback()
        print(f"Weekly refresh failed: {error}", flush=True)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
