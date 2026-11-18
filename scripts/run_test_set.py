import time
from agent import pipeline
from config import settings

TEST_FOLDER = settings.ROOT / "sample_data" / "test_set"
JOB_NAME = "backend_python_developer"


def main():
    if settings.DB_PATH.exists():
        settings.DB_PATH.unlink()
        print("Old database deleted")

    start = time.time()
    pipeline.run(TEST_FOLDER, JOB_NAME, pattern="resume_*.txt")
    minutes = (time.time() - start) / 60
    print(f"Total time: {minutes:.1f} minutes")


if __name__ == "__main__":
    main()