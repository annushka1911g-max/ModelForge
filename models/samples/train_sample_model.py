"""
Train a sample Iris classification model for ModelForge demo.
Saves model as joblib artifact.
"""
import os
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def train_and_save():
    # Load dataset
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Iris model accuracy: {accuracy:.4f}")

    # Save
    output_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(output_dir, "iris_model.joblib")
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")

    # Feature schema for ModelForge registration
    feature_schema = [
        {"name": "sepal_length", "type": "float", "required": True},
        {"name": "sepal_width", "type": "float", "required": True},
        {"name": "petal_length", "type": "float", "required": True},
        {"name": "petal_width", "type": "float", "required": True},
    ]
    print(f"Feature schema: {feature_schema}")

    # Sample prediction input
    sample_input = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    pred = model.predict([list(sample_input.values())])
    print(f"Sample prediction: {pred[0]} (class={iris.target_names[pred[0]]})")

    return model_path, feature_schema


if __name__ == "__main__":
    train_and_save()
