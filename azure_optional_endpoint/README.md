# Optional production Azure endpoint architecture

These files are retained only to demonstrate how the classifier could be deployed in an unrestricted production Azure subscription.

They are **not part of the default SHU runtime**. The Sheffield Hallam lab policy observed during development denied `Microsoft.MachineLearningServices/workspaces/onlineEndpoints`, so Flask defaults to local inference.

Do not place endpoint keys in source control. If a future environment permits managed online endpoints, review and update these YAML/SDK files before deployment.
