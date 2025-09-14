from pathlib import Path
import website_learning.main as app

BASE_DIR = Path(__file__).parent
app.main(BASE_DIR / "example_config.yaml")
