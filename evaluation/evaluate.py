import json
from app.sop import match_sops, select_sop

def evaluate():
    with open("evaluation/dataset.json") as file:
        dataset = json.load(file)

    correct = 0

    for item in dataset:
        matches = match_sops(
            item["activity"],
            item["weather"]
        )

        result = select_sop(matches)
        selected = result["selected_sop"]

        actual_sop = selected.get("id")
        actual_decision = result["decision"]["decision"]

        sop_ok = actual_sop == item["expected_sop"]
        decision_ok = actual_decision == item["expected_decision"]

        if sop_ok and decision_ok:
            correct += 1

        print("\nQUERY:", item["query"])
        print("EXPECTED SOP:", item["expected_sop"])
        print("ACTUAL SOP:", actual_sop)
        print("EXPECTED DECISION:", item["expected_decision"])
        print("ACTUAL DECISION:", actual_decision)
        print("PASS:", sop_ok and decision_ok)

    accuracy = correct / len(dataset)

    print("\nEVALUATION")
    print(f"Correct: {correct}/{len(dataset)}")
    print(f"Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    evaluate()