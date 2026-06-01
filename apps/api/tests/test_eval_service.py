import os
import tempfile
import unittest
from pathlib import Path
import json

from app.models.schemas import DatasetRunRequest, EvalCase, EvaluationRunCreate, PromptVersionCreate
from app.services.eval_service import EvalService


class EvalServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_path = Path(self.temp_dir.name) / "store.json"
        self.service = EvalService()
        self.service._prompts = {}
        self.service._runs = {}
        self.service._store_path = self.store_path

        self.project_root = Path(self.temp_dir.name)
        self.evals_dir = self.project_root / "evals"
        self.evals_dir.mkdir(parents=True, exist_ok=True)
        sample_dataset = [
            {
                "input": "Summarize security access policy",
                "expected_keywords": ["policy", "security", "access"],
            }
        ]
        (self.evals_dir / "sample_suite.json").write_text(json.dumps(sample_dataset), encoding="utf-8")
        os.environ["LLM_EVAL_PROJECT_ROOT"] = str(self.project_root)

    def tearDown(self) -> None:
        os.environ.pop("LLM_EVAL_PROJECT_ROOT", None)
        self.temp_dir.cleanup()

    def test_prompt_registry_and_eval_run(self) -> None:
        prompt = self.service.create_prompt(
            PromptVersionCreate(
                name="Policy Copilot",
                version="1.0.0",
                system_prompt="Use only approved policy context and keep responses grounded.",
                owner="quality-team",
                model="gpt-4.1-mini",
                risk_level="high",
            )
        )

        run = self.service.run_evaluation(
            EvaluationRunCreate(
                prompt_id=prompt.id,
                dataset_name="smoke-suite",
                eval_cases=[
                    EvalCase(
                        input="Summarize policy controls for production access.",
                        expected_keywords=["policy", "production", "controls"],
                    )
                ],
            )
        )

        self.assertIn(run.run.status, {"passed", "blocked"})
        self.assertGreaterEqual(len(run.run.cases), 1)
        scorecards = self.service.list_scorecards().scorecards
        self.assertEqual(len(scorecards), 1)
        self.assertEqual(scorecards[0].prompt_id, prompt.id)

    def test_analytics_counts_runs(self) -> None:
        prompt = self.service.create_prompt(
            PromptVersionCreate(
                name="Security Copilot",
                version="0.9.0",
                system_prompt="Summarize controls with grounded policy context.",
                owner="security",
                model="claude-3.5-sonnet",
                risk_level="critical",
            )
        )

        self.service.run_evaluation(
            EvaluationRunCreate(
                prompt_id=prompt.id,
                dataset_name="quality-suite",
                eval_cases=[EvalCase(input="List controls", expected_keywords=["controls"])],
            )
        )

        analytics = self.service.analytics()
        self.assertEqual(analytics.prompt_count, 1)
        self.assertEqual(analytics.run_count, 1)

    def test_dataset_listing_reads_eval_files(self) -> None:
        datasets = self.service.list_datasets().datasets

        self.assertTrue(any(dataset.name == "sample_suite" for dataset in datasets))

    def test_run_from_dataset_creates_run(self) -> None:
        prompt = self.service.create_prompt(
            PromptVersionCreate(
                name="Dataset Copilot",
                version="1.2.0",
                system_prompt="Use policy context and avoid unsupported claims.",
                owner="qa",
                model="gpt-4.1-mini",
                risk_level="high",
            )
        )

        run = self.service.run_from_dataset(
            DatasetRunRequest(
                prompt_id=prompt.id,
                dataset_name="sample_suite",
                max_cases=5,
            )
        )

        self.assertEqual(run.run.dataset_name, "sample_suite")
        self.assertGreaterEqual(len(run.run.cases), 1)



if __name__ == "__main__":
    unittest.main()
