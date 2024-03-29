import json
import random
from belief.models import *
import dotenv

dotenv.load_dotenv()


def run(true_evidence="strong", false_evidence="weak", n=10):
    results = {
        "correct": 0.0,
        "incorrect": 0.0,
        "revised": 0.0,
        "no_revised": 0.0,
        "revised_and_correct": 0.0,
        "revised_and_incorrect": 0.0,
        "no_revised_and_correct": 0.0,
        "no_revised_and_incorrect": 0.0,
        "total": 0.0,
    }
    for i in range(n):
        # randomly pick A or B
        true_box = random.choice(["A", "B"])
        false_box = "A" if true_box == "B" else "B"
        experiment = Experiment(true_box)
        # randomly show true or false evidence first
        # true evidence is always the true box
        if random.choice([true_evidence, false_evidence]) == false_evidence:
            experiment.add_evidence(false_evidence, false_box)
            experiment.add_evidence(true_evidence, true_box)
        else:
            experiment.add_evidence(true_evidence, true_box)
            experiment.add_evidence(false_evidence, false_box)

        try:
            result = experiment.run_experiment()
        except Exception as e:
            print(e)
            continue
        results["total"] += 1
        if result["correct"]:
            results["correct"] += 1
            if result["revised"]:
                results["revised_and_correct"] += 1
                results["revised"] += 1
            elif not result["revised"]:
                results["no_revised"] += 1
                results["no_revised_and_correct"] += 1
        else:
            results["incorrect"] += 1
            if result["revised"]:
                results["revised_and_incorrect"] += 1
                results["revised"] += 1
            elif not result["revised"]:
                results["no_revised_and_incorrect"] += 1
                results["no_revised"] += 1

    # format results - % correct, % correct when revised, % correct when not revised
    percent_results = {
        "correct": results["correct"] / results["total"],
        "revised_and_correct": results["revised_and_correct"] / results["revised"]
        if results["revised"] > 0
        else 0,
        "no_revised_and_correct": results["no_revised_and_correct"]
        / results["no_revised"]
        if results["no_revised"] > 0
        else 0,
    }
    print(json.dumps(percent_results))


if __name__ == "__main__":
    run("strong", "weak")
    # run("medium", "weak")
