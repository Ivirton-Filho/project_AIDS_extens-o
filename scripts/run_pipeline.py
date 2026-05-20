import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.hiv_dashboard.data.step3_transform import consolidar

if __name__ == "__main__":
    consolidar()
