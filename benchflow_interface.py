import json
import os
from typing import Any, Dict

from datasets import load_dataset

from benchflow import BaseBench
from benchflow.schemas import BenchArgs, BenchmarkResult
from inspect_ai.log import list_eval_logs, read_eval_log


class InspectEvalBench(BaseBench):
    def get_args(self, task_id: str) -> BenchArgs:
        return BenchArgs(None)

    def get_image_name(self) -> str:
        return "huangjianzhao/benchflow:inspect_evals"

    def get_results_dir_in_container(self) -> str:
        return "/app/logs"

    def get_log_files_dir_in_container(self) -> str:
        return "/app/tmp" # Useless

    def get_result(self, task_id: str) -> BenchmarkResult:
        # TODO: do not import inspect_ai
        try:
            for eval_log in list_eval_logs(self.get_results_dir_in_container()):
                for sample in read_eval_log(eval_log.name).samples:
                    if sample.id == (task_id + 1):
                        return BenchmarkResult(
                            task_id=task_id,
                            is_resolved=True,
                            metrics={"score": sample.score},
                            log=sample.messages,
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
        self.run_bench(0, "", {})
        eval_log = read_eval_log(list_eval_logs(self.get_results_dir_in_container())[0].name)
        return {"task_ids": list(range(len(eval_log.eval.dataset.samples))), "error_message": ""}
    
    def cleanup(self):
        pass