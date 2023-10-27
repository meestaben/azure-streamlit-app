# Copyright 2016-2020, Pulumi Corporation.  All rights reserved.

import pulumi
import pulumi_azure_native.containerregistry as containerregistry
import pulumi_azure_native.resources as resources
import pulumi_azure_native.insights as insights
import pulumi_azure_native.web as web
import pulumi_docker as docker

environment = pulumi.get_stack()
subscription_id = pulumi.Config("azure-native").get("subscription_id")

resource_group = resources.ResourceGroup(
    f"rg-app-{environment}-us-001",
)

plan = web.AppServicePlan(
    f"plan-app-{environment}-us-001",
    resource_group_name=resource_group.name,
    kind="Linux",
    reserved=True,
    sku=web.SkuDescriptionArgs(
        name="S1",
        tier="Standard",
    )
)

custom_image = "streamlit-app"
registry = containerregistry.Registry(
    f"crapp{environment}us001",
    resource_group_name=resource_group.name,
    sku=containerregistry.SkuArgs(
        name="Basic",
    ),
    admin_user_enabled=True)

credentials = containerregistry.list_registry_credentials_output(resource_group_name=resource_group.name,
                                                                 registry_name=registry.name)
admin_username = credentials.username
admin_password = credentials.passwords[0]["value"]

my_image = docker.Image(
    custom_image,
    image_name=registry.login_server.apply(
        lambda login_server: f"{login_server}/{custom_image}:v1.0.0"),
    build=docker.DockerBuild(context=f"./app"),
    registry=docker.ImageRegistry(
        server=registry.login_server,
        username=admin_username,
        password=admin_password
    ),
)

streamlit_app = web.WebApp(
    f"app-slt-{environment}-us-001",
    resource_group_name=resource_group.name,
    server_farm_id=plan.id,
    site_config=web.SiteConfigArgs(
        app_settings=[
            web.NameValuePairArgs(name="WEBSITES_ENABLE_APP_SERVICE_STORAGE", value="false"),
            web.NameValuePairArgs(name="DOCKER_REGISTRY_SERVER_URL",
                                  value=registry.login_server.apply(
                                      lambda login_server: f"https://{login_server}")),
            web.NameValuePairArgs(name="DOCKER_REGISTRY_SERVER_USERNAME",
                                  value=admin_username),
            web.NameValuePairArgs(name="DOCKER_REGISTRY_SERVER_PASSWORD",
                                  value=admin_password),
            web.NameValuePairArgs(name="WEBSITES_PORT", value="8501"),
        ],
        always_on=True,
        linux_fx_version=my_image.image_name.apply(lambda image_name: f"DOCKER|{image_name}"),
    ),
    https_only=True)


# Configure memory-based autoscale
autoscale_setting = insights.AutoscaleSetting('AutoScaleSetting',
    resource_group_name=resource_group.name,
    target_resource_uri=plan.id,
    location=streamlit_app.location,
    enabled=True,
    profiles=[
        {
            "capacity":insights.ScaleCapacityArgs(
                default="1",
                maximum="5",
                minimum="1",
            ),
            "name": "AutoScaleProfile",
            "rules": [
                {
                    "metricTrigger":insights.MetricTriggerArgs(
                        divide_per_instance=False,
                        metric_namespace="Microsoft.Web/serverfarms",
                        metric_name="CpuPercentage",
                        metric_resource_uri=plan.id,
                        operator=insights.ComparisonOperationType.GREATER_THAN,
                        statistic=insights.MetricStatisticType.AVERAGE,
                        threshold=70,
                        time_aggregation=insights.TimeAggregationType.AVERAGE,
                        time_grain="PT1M",
                        time_window="PT5M",
                    ),
                    "scaleAction":insights.ScaleActionArgs(
                        cooldown="PT5M",
                        direction=insights.ScaleDirection.INCREASE,
                        type=insights.ScaleType.CHANGE_COUNT,
                        value="1",
                    ),
                },
                {
                    "metricTrigger":insights.MetricTriggerArgs(
                        divide_per_instance=False,
                        metric_namespace="Microsoft.Web/serverfarms",
                        metric_name="CpuPercentage",
                        metric_resource_uri=plan.id,
                        operator=insights.ComparisonOperationType.GREATER_THAN,
                        statistic=insights.MetricStatisticType.AVERAGE,
                        threshold=80,
                        time_aggregation=insights.TimeAggregationType.AVERAGE,
                        time_grain="PT2M",
                        time_window="PT5M",
                    ),
                    "scaleAction":insights.ScaleActionArgs(
                        cooldown="PT6M",
                        direction=insights.ScaleDirection.DECREASE,
                        type=insights.ScaleType.CHANGE_COUNT,
                        value="2",
                    ),
                },
            ],
        },
    ],
)

pulumi.export(
    "endpoint",
    streamlit_app.default_host_name.apply(lambda default_host_name: f"https://{default_host_name}"))
