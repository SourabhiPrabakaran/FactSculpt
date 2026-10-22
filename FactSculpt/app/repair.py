import os
import sys
import json
import argparse
from typing import Dict, Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from factsculpt.repair.pipeline import AttributeTargetedRepairPipeline

def read_text_or_file(input_val: str) -> str:
    if os.path.isfile(input_val):
        with open(input_val, "r", encoding="utf-8") as f:
            return f.read().strip()
    return input_val.strip()

def main():
    parser = argparse.ArgumentParser(description="FactSculpt: Attribute-Targeted Repair CLI")
    parser.add_argument("--source", type=str, required=True, help="Path to source text file or raw source text")
    parser.add_argument("--enhanced", type=str, required=True, help="Path to enhanced text file or raw enhanced text")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum repair iterations (default: 3)")
    args = parser.parse_args()

    src_text = read_text_or_file(args.source)
    gen_text = read_text_or_file(args.enhanced)

    repair_pipeline = AttributeTargetedRepairPipeline(max_iterations=args.max_iterations)
    result = repair_pipeline.repair(src_text, gen_text)

    output = {
        "original_source": result.original_source,
        "initial_enhanced": result.initial_enhanced,
        "repaired_text": result.repaired_text,
        "iterations_run": result.iterations_run,
        "stopped_reason": result.stopped_reason,
        "initial_classification": result.initial_classification,
        "final_classification": result.final_classification,
        "initial_severity": result.initial_severity,
        "final_severity": result.final_severity,
        "steps": [s.model_dump() for s in result.steps]
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
