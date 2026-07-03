import contextlib
import tempfile
from git import Repo
from typing import Generator

class GitService:
    @contextlib.contextmanager
    def clone_repository(self, repo_url: str) -> Generator[str, None, None]:
        """Clones a repository into a temporary directory and cleans it up after use."""
        with tempfile.TemporaryDirectory() as temp_dir:
            Repo.clone_from(repo_url, temp_dir)
            yield temp_dir
