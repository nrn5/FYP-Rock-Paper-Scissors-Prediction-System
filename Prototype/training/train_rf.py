# { TRAIN RANDOM FOREST MODEL ON GESTURE DATA }

import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, accuracy_score,
                             confusion_matrix, ConfusionMatrixDisplay)
from config.paths import RF_DATA_PATH, GESTURE_RF_PATH

def load_data(path: str):
    data = pd.read_csv(path)
    X = data.drop("label", axis=1)
    Y = data["label"]
    return X, Y

def build_model():
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42
    )

def train_model(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y,test_size=0.2,random_state=42,stratify=y)
    model = build_model()
    model.fit(x_train, y_train)

    return model, x_test, y_test

def evaluate_model(model, x_test, y_test):
    y_pred = model.predict(x_test)
    # some basic mestric
    acc = accuracy_score(y_test, y_pred)
    print(f"\n[train_rf.py] Accuracy: {acc:.4f}")
    print("\n[train_rf.py] Classification report:\n")
    print(classification_report(y_test, y_pred))

    # {CONFUSION MATRIX}
    labels = sorted(y_test.unique())

    cm = confusion_matrix(y_test, y_pred, labels=labels)
    cm_norm = cm.astype("float") / cm.sum(axis=1, keepdims=True)

    print("\n[train_rf.py] Confusion matrix:\n", cm)

    # plot confusion matrix no normalsieaion yet
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot()
    plt.title("Confusion Matrix")
    plt.show()

    # plot normalised confusion matrix
    disp_norm = ConfusionMatrixDisplay(confusion_matrix=cm_norm, display_labels=labels)
    disp_norm.plot()
    plt.title("Normalised Confusion Matrix")
    plt.show()

    # { PER CLASS ACCURACY }
    print("\n[train_rf.py] Per class accuracy:")
    for i, label in enumerate(labels):
        class_acc = cm[i, i] / cm[i].sum() if cm[i].sum() > 0 else 0
        print(f"{label}: {class_acc:.2%}")

    # { CONFIDENCE ANALYSIS }
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(x_test)
        confidences = np.max(probs, axis=1)
        print(f"\n[train_rf.py] Average confidence: {np.mean(confidences):.3f}")

        # low confidence predictions
        low_conf_idx = np.where(confidences < 0.6)[0]
        print(f"\n[train_rf.py] Low confidence predictions (<0.6): {len(low_conf_idx)}")

    # { ERROR ANALYSIS }
    print("\n[train_rf.py] Sample misclassifications:")
    mistakes = np.where(y_pred != y_test)[0]

    for i in mistakes[:10]:  # show first 10 mistakes
        print(f"True: {y_test.iloc[i]} | Pred: {y_pred[i]}")

def save_model(model, path: str):
    joblib.dump(model, path)
    print(f"\n[train_rf.py] Model saved")

def run_training():
    """ entry point """
    print("\n[train_rf.py] Loading data...")
    X, Y = load_data(RF_DATA_PATH)

    print("\n[train_rf.py] Training model...")
    model, x_test, Y_test = train_model(X, Y)

    print("\n[train_rf.py] Evaluating")
    evaluate_model(model, x_test, Y_test)

    print("\n[train_rf.py] Saving model...")
    save_model(model, GESTURE_RF_PATH)

# { MAIN ENTRY }
if __name__ == "__main__":
    run_training()
