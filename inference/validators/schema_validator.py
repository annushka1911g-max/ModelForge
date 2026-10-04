
"""
Feature schema validation for ModelForge inference requests.
"""

from typing import Any, Dict, Tuple, List


class FeatureSchemaValidator:

    @staticmethod
    def validate(
        features: Dict[str, Any],
        feature_schema: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Validate incoming prediction features against the stored
        model feature schema.

        Expected feature_schema format:

        {
            "features": [
                {
                    "name": "sepal_length",
                    "type": "float"
                },
                {
                    "name": "sepal_width",
                    "type": "float"
                }
            ]
        }
        """

        errors: List[str] = []

        # ---------------------------------------------------------
        # 1. Validate schema structure
        # ---------------------------------------------------------
        if not isinstance(feature_schema, dict):
            return False, ["Feature schema must be a dictionary"]

        schema_features = feature_schema.get("features")

        if not isinstance(schema_features, list):
            return False, [
                "Feature schema must contain a 'features' list"
            ]

        # ---------------------------------------------------------
        # 2. Validate that request features are a dictionary
        # ---------------------------------------------------------
        if not isinstance(features, dict):
            return False, [
                "Prediction features must be provided as a JSON object"
            ]

        # ---------------------------------------------------------
        # 3. Validate every expected feature
        # ---------------------------------------------------------
        expected_feature_names = set()

        for field_def in schema_features:

            if not isinstance(field_def, dict):
                errors.append(
                    f"Invalid feature definition: {field_def}"
                )
                continue

            name = field_def.get("name")
            expected_type = field_def.get("type")

            if not name:
                errors.append(
                    "Feature definition is missing 'name'"
                )
                continue

            expected_feature_names.add(name)

            # Missing feature
            if name not in features:
                errors.append(
                    f"Missing required feature: {name}"
                )
                continue

            value = features[name]

            # -----------------------------------------------------
            # 4. Validate data type
            # -----------------------------------------------------
            if expected_type == "float":

                # Python bool is technically an int, so explicitly
                # reject it.
                if isinstance(value, bool) or not isinstance(
                    value, (int, float)
                ):
                    errors.append(
                        f"Feature '{name}' must be a float"
                    )

            elif expected_type == "int":

                if isinstance(value, bool) or not isinstance(
                    value, int
                ):
                    errors.append(
                        f"Feature '{name}' must be an integer"
                    )

            elif expected_type == "str":

                if not isinstance(value, str):
                    errors.append(
                        f"Feature '{name}' must be a string"
                    )

            elif expected_type == "bool":

                if not isinstance(value, bool):
                    errors.append(
                        f"Feature '{name}' must be a boolean"
                    )

        # ---------------------------------------------------------
        # 5. Reject unexpected features
        # ---------------------------------------------------------
        unexpected_features = (
            set(features.keys()) - expected_feature_names
        )

        for name in unexpected_features:
            errors.append(
                f"Unexpected feature: {name}"
            )

        # ---------------------------------------------------------
        # 6. Return validation result
        # ---------------------------------------------------------
        return len(errors) == 0, errors

