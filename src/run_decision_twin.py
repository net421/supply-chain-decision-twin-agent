import argparse
import json

from src.decision_twin import run_decision_twin


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic supply-chain decision twin scenario.")
    parser.add_argument(
        "--scenario",
        default="demand_spike_supplier_delay",
        choices=[
            "baseline",
            "demand_spike",
            "supplier_delay",
            "demand_spike_supplier_delay",
        ],
    )
    parser.add_argument("--product-id")
    parser.add_argument("--location-id")
    parser.add_argument("--no-persist", action="store_true")
    args = parser.parse_args()

    result = run_decision_twin(
        args.scenario,
        product_id=args.product_id,
        location_id=args.location_id,
        persist=not args.no_persist,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
