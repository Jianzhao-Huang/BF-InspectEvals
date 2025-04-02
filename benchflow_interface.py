import json
import os
from typing import Any, Dict

from datasets import load_dataset

from benchflow import BaseBench
from benchflow.schemas import BenchArgs, BenchmarkResult


class InspectEvalBench(BaseBench):
    def get_args(self, task_id: str) -> BenchArgs:
        arguments = {
            "required": ["BENCHMARK_NAME"],
        }
        return BenchArgs(arguments)

    def get_image_name(self) -> str:
        return "huangjianzhao/benchflow:inspect_evals"

    def get_results_dir_in_container(self) -> str:
        return "/app/logs"

    def get_log_files_dir_in_container(self) -> str:
        return "/app/tmp" # Useless

    def get_result(self, task_id: str) -> BenchmarkResult:
        # TODO: do not import inspect_ai
        try:
            for log_file in os.listdir(self.results_dir):
                if not log_file.endswith('.json'):
                    continue
                with open(os.path.join(self.results_dir, log_file)) as f:
                    eval_data = json.load(f)
                    for sample in eval_data['samples']:
                        if sample['id'] == (int(task_id) + 1):
                            return BenchmarkResult(
                                task_id=task_id,
                                is_resolved=True,
                                metrics=list(sample['scores'].items())[0][1]['value'],
                                log={"trace": sample['messages']},
                                other={},
                            )
            else:
                raise Exception(f"No eval log found for task_id: {task_id}")
        
        except Exception as e:
            return BenchmarkResult(
                task_id=task_id,
                is_resolved=False,
                metrics={"score": 0},
                log={"error": str(e)},
                other={"error": str(e)},
            )

        
    def get_all_tasks(self, split: str) -> Dict[str, Any]:
        # self.run_bench(0, "", {})
        for log_file in os.listdir(self.results_dir):
            if not log_file.endswith('.json'):
                continue
            with open(os.path.join(self.results_dir, log_file)) as f:
                eval_log = json.load(f)
                break
        return {"task_ids": [str(i) for i in range(eval_log["eval"]["dataset"]["samples"])], "error_message": ""}
    
    def cleanup(self):
        pass