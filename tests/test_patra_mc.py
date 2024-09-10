import jsonschema

from patra_model_card.patra_model_card import (AIModel, BiasAnalysis,
                                               ExplainabilityAnalysis, Metric,
                                               ModelCard, ModelCardJSONEncoder)
import json
import unittest
from jsonschema import validate
import os.path

SCHEMA_JSON = os.path.join(os.path.dirname(__file__), os.pardir, 'patra_model_card/schema/schema.json')

class ModelCardTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.aimodel = AIModel(name="DenseNet",
                               version="v0.1",
                               description="DenseNet CNN model",
                               owner="PyTorch",
                               location="pytorch.org",
                               license="testLicence",
                               framework="tensorflow",
                               model_type="cnn",
                               test_accuracy=0.89)
        self.bias_analysis = BiasAnalysis(0.1, 0.2)
        self.xai_analysis = ExplainabilityAnalysis(
            "XAI Test 2", [Metric("xai1", "0.5"),
                           Metric("xai2", "0.8")])

        self.mc = ModelCard(
            name="icicle-camera-traps",
            version="0.1",
            short_description="Camera Traps CNN inference model card",
            full_description="Camera Traps CNN full descr inference model card",
            keywords="cnn, pytorch, icicle",
            author="Joe",
            input_data="cifar10",
            input_type="image",
            output_data="None",
            category="classification",
            ai_model=self.aimodel,
            bias_analysis=self.bias_analysis,
            xai_analysis=self.xai_analysis)
        self.mc_save_location = "./test_mc.json"

    def test_json_serialization(self):
        """
        This tests whether the python classes can be serialized to JSON.
        """
        # Convert the dataclass object to JSON string using the custom encoder
        mc_json = json.dumps(self.mc, cls=ModelCardJSONEncoder, indent=2)

        # Parse the JSON string back to a dictionary
        parsed_mc = json.loads(mc_json)

        self.assertEqual(parsed_mc['name'], "icicle-camera-traps")
        self.assertEqual(parsed_mc['ai_model']['name'], "DenseNet")
        self.assertEqual(
            parsed_mc['bias_analysis']['demographic_parity_difference'], 0.1)

    def test_schema_compatibility(self):
        """
        This tests whether the serialized JSON is compatible with the schema.
        """
        # Convert the dataclass object to JSON string using the custom encoder
        mc_json = json.dumps(self.mc, cls=ModelCardJSONEncoder, indent=4)

        with open(SCHEMA_JSON, 'r') as schema_file:
            schema = json.load(schema_file)
        try:
            validate(json.loads(mc_json), schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Validation Error: {e}")

    def test_validate(self):
        """
        This tests the validate function.
        """
        is_valid = self.mc.validate()
        self.assertTrue(is_valid)

    def test_framework_enum(self):
        """
        This tests the framework enum.
        """
        mc = ModelCard(
            name="icicle-camera-traps",
            version="0.1",
            short_description="Camera Traps CNN inference model card",
            full_description="Camera Traps CNN full descr inference model card",
            keywords="cnn, pytorch, icicle",
            author="Joe",
            input_data="cifar10",
            input_type="image",
            output_data="None",
            category="classification")

        aimodel = AIModel(name="DenseNet",
                          version="v0.1",
                          description="DenseNet CNN model",
                          owner="PyTorch",
                          location="pytorch.org",
                          license="testLicence",
                          framework="keras",
                          model_type="dnn",
                          test_accuracy=0.89)
        bias_analysis = BiasAnalysis(0.1, 0.2)

        mc.ai_model = aimodel
        mc.bias_analysis = bias_analysis

        is_valid = mc.validate()
        self.assertFalse(is_valid)

    def test_json_conversion(self):
        """
        This tests if the JSON conversion works
        """
        # Convert the dataclass object to JSON string using the custom encoder
        mc_json = json.dumps(self.mc, cls=ModelCardJSONEncoder, indent=4)

        # convert the json string back to python model
        mc_converted = json.loads(mc_json)

        self.assertEqual(mc_converted['input_data'], "cifar10")

    def test_json_save(self):
        """
        This tests if the JSON file can be saved
        """
        self.mc.save(self.mc_save_location)

        # file existing verification
        self.assertTrue(os.path.exists(self.mc_save_location),
                        "File not found")

        # Verify the content in the file is same as the saved data
        with open(self.mc_save_location, 'r') as json_file:
            saved_data = json.load(json_file)

        self.assertEqual(
            saved_data['name'], self.mc.name,
            "Saved JSON data doesn't match the original Model Card")

    def tearDown(self):
        # Removing the saved file for the model card
        if os.path.exists(self.mc_save_location):
            os.remove(self.mc_save_location)


if __name__ == '__main__':
    unittest.main()
