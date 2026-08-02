# DVC integration for llm-eval-guardrails-platform

import dvc.api
import dvc.repo
from typing import Dict, Any, List
import os

class DVCService:
    def __init__(self):
        self.repo_url = os.getenv("DVC_REPO_URL")
        self.repo_path = os.getenv("DVC_REPO_PATH", ".")
        self.repo = dvc.repo.Repo(self.repo_path)

    def add(self, path: str):
        """Add a file/directory to DVC"""
        self.repo.add(path)
        return {"status": "added", "path": path}

    def commit(self, message: str):
        """Commit DVC changes"""
        self.repo.commit(message)
        return {"status": "committed", "message": message}

    def push(self, remote: str = "origin"):
        """Push DVC data to remote"""
        self.repo.push(remote=remote)
        return {"status": "pushed", "remote": remote}

    def pull(self, remote: str = "origin"):
        """Pull DVC data from remote"""
        self.repo.pull(remote=remote)
        return {"status": "pulled", "remote": remote}

    def status(self):
        """Get DVC status"""
        return self.repo.status()

    def diff(self, target: str = None):
        """Get DVC diff"""
        return self.repo.diff(target=target)

    def metrics_show(self, targets: List[str] = None):
        """Show metrics"""
        return self.repo.metrics.show(targets=targets)

    def metrics_add(self, path: str):
        """Add metrics file"""
        self.repo.metrics.add(path)
        return {"status": "added", "path": path}

    def params_show(self, targets: List[str] = None):
        """Show parameters"""
        return self.repo.params.show(targets=targets)

    def params_diff(self, targets: List[str] = None):
        """Show parameter diff"""
        return self.repo.params.diff(targets=targets)

    def experiments_show(self):
        """Show experiments"""
        return self.repo.experiments.show()

    def experiments_new(self, name: str, params: Dict[str, Any] = None):
        """Create new experiment"""
        return self.repo.experiments.new(name=name, params=params)

    def get_file(self, path: str, repo: str = None, rev: str = None):
        """Get file from DVC remote"""
        return dvc.api.read(
            path=path,
            repo=repo or self.repo_url,
            rev=rev
        )

    def get_url(self, path: str, repo: str = None, rev: str = None):
        """Get URL for file in DVC remote"""
        return dvc.api.get_url(
            path=path,
            repo=repo or self.repo_url,
            rev=rev
        )
