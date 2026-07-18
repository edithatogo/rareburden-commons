from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_raw_data_directories_contain_only_notices() -> None:
    for directory in ("raw", "interim", "processed"):
        files = [path.name for path in (ROOT / "data" / directory).iterdir() if path.is_file()]
        assert files == ["README.md"]
