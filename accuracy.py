accuracy_data = {
    "total": 0,
    "correct": 0
}

def update_accuracy(total, correct):
    accuracy_data["total"] += total
    accuracy_data["correct"] += correct

def get_accuracy():
    if accuracy_data["total"] == 0:
        return 0
    return round((accuracy_data["correct"] / accuracy_data["total"]) * 100, 2)
