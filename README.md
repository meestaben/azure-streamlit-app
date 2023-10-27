[![Deploy](https://get.pulumi.com/new/button.svg)](https://app.pulumi.com/new?template=https://github.com/pulumi/examples/blob/master/azure-py-appservice-docker/README.md)

# Azure App Service - Autoscaling Streamlit PoC

Deploys a new custom registry in Azure Container Registry, builds a custom Docker image, and runs the image from the custom registry. The image contains a Streamlit demo app.

## Running the App

1. Create a new stack:

    ```bash
    $ pulumi stack init dev
    ```

1. Login to Azure CLI (you will be prompted to do this during deployment if you forget this step):

    ```bash
    $ az login
    ```
   
1. Create a Python virtualenv, activate it, and install dependencies:

   This installs the dependent packages [needed](https://www.pulumi.com/docs/intro/concepts/how-pulumi-works/) for our Pulumi program.

    ```bash
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip3 install -r requirements.txt
    ```

1. Specify the Azure location to use:

    ```bash
    $ pulumi config set azure-native:location uksouth
    ```

1. Run `pulumi up` to preview and deploy changes:

    ```bash
    $ pulumi up
    Previewing changes:
    ...

    Performing changes:
    ...
    Resources:
        + 5 created

    Duration: 56s
    ```

1. Check the deployed endpoints:

    ```bash
    $ open $(pulumi stack output endpoint)

    ```

## Building the app locally to test

```
cd app
docker build -t streamlit-app:latest .
docker run -p 8501:8501 streamlit-app:latest
open "http://localhost:8501"
```

## Limitations
1.  PoC uses default Azure domain. In production it will require custom domain and SSL/TLS cert

2.  Single dev environment only at present

3.  Streamlit's in-memory state handling is potentially not compatible with a scale in/out model in which backend resources are generally considered to be ephemeral. Requires testing.
