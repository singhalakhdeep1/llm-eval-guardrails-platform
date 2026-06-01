import json
from pathlib import Path

from app.models.schemas import DatasetRunRequest
from app.services.eval_service import eval_service


def run_smoke() -> dict:
    prompts = eval_service.list_prompts().prompts
    if not prompts:
        raise RuntimeError("No prompts are available in the registry")

    datasets = eval_service.list_datasets().datasets
    if not datasets:
        raise RuntimeError("No datasets found under evals/")

    selected_prompt = prompts[0]
    selected_dataset = datasets[0]
    run = eval_service.run_from_dataset(
        DatasetRunRequest(
            prompt_id=selected_prompt.id,
            dataset_name=selected_dataset.name,
            max_cases=min(10, selected_dataset.case_count),
        )
    )

    output = {
        "prompt": f"{selected_prompt.name} v{selected_prompt.version}",
        "dataset": selected_dataset.name,
        "status": run.run.status,
        "pass_rate": run.run.pass_rate,
        "cases": len(run.run.cases),
    }

    output_path = Path(__file__).resolve().parents[1] / "data" / "dataset_smoke_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(json.dumps(run_smoke(), indent=2))
