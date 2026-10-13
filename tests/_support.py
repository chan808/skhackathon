"""Keep test scratch files inside the authorized project workspace."""
import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def workspace_temp():
    base = Path(__file__).absolute().parents[1] / ".cache" / "test-temp"
    base.mkdir(parents=True, exist_ok=True)
    temporary = tempfile.TemporaryDirectory(dir=str(base))
    generated = Path(temporary.name).absolute()
    if not generated.is_relative_to(base.absolute()):
        raise RuntimeError("Test scratch path escaped the project cache")
    try:
        yield str(generated)
    finally:
        temporary.cleanup()
