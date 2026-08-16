import argparse
from pathlib import Path

from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineDeployment, ManagedOnlineEndpoint, Model, Environment, CodeConfiguration
from azure.identity import DefaultAzureCredential


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--subscription-id", required=True)
    p.add_argument("--resource-group", required=True)
    p.add_argument("--workspace", required=True)
    p.add_argument("--endpoint", default="customer-intelligence-endpoint")
    args = p.parse_args()

    root = Path(__file__).resolve().parents[1]
    ml_client = MLClient(
        DefaultAzureCredential(), args.subscription_id, args.resource_group, args.workspace
    )

    model = ml_client.models.create_or_update(
        Model(path=str(root / "artifacts" / "complaint_classifier.joblib"), name="customer-intelligence-classifier")
    )
    env = ml_client.environments.create_or_update(
        Environment(
            name="customer-intelligence-inference",
            conda_file=str(root / "azure" / "environment.yml"),
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
        )
    )
    endpoint = ManagedOnlineEndpoint(name=args.endpoint, auth_mode="key")
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    deployment = ManagedOnlineDeployment(
        name="blue",
        endpoint_name=args.endpoint,
        model=model,
        environment=env,
        code_configuration=CodeConfiguration(
            code=str(root / "azure"), scoring_script="score.py"
        ),
        instance_type="Standard_DS3_v2",
        instance_count=1,
    )
    ml_client.online_deployments.begin_create_or_update(deployment).result()
    endpoint.traffic = {"blue": 100}
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()
    print(f"Deployed endpoint: {args.endpoint}")


if __name__ == "__main__":
    main()
