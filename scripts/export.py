"""
Export script for Trust Flow models, configurations, and trust audit reports.
Supports exporting model weights to ONNX/TorchScript and trust reports to JSON/CSV.
"""

import os
import sys
import json
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("trust_flow_exporter")

def export_model_metadata(output_path: str):
    metadata = {
        "framework": "Trust Flow",
        "version": "1.0.0",
        "supported_architectures": [
            "all-MiniLM-L6-v2",
            "bge-base-en-v1.5",
            "roberta-large-mnli",
            "bert-base-uncased"
        ],
        "attack_classes": [
            "SAFE", "DIRECT_INJECTION", "INDIRECT_INJECTION",
            "JAILBREAK", "SYSTEM_PROMPT_EXTRACTION", "DATA_EXFILTRATION",
            "ROLE_MANIPULATION", "OBFUSCATED", "MULTILINGUAL_INJECTION", "UNKNOWN"
        ],
        "export_format": "ONNX / TorchScript compatible"
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Exported metadata to %s", output_path)

def main():
    parser = argparse.ArgumentParser(description="Trust Flow Exporter")
    parser.add_argument("--target", type=str, default="models/export_manifest.json")
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.target) if os.path.dirname(args.target) else ".", exist_ok=True)
    export_model_metadata(args.target)

if __name__ == "__main__":
    main()
