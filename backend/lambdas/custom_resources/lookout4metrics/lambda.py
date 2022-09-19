# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import logging
import uuid
import cfnresponse
from crhelper import CfnResource

logger = logging.getLogger(__name__)
helper = CfnResource(log_level="INFO")
L4M = boto3.client("lookoutmetrics")


def create_detector(project_name, frequency):
    response_create = ''

    response_create = L4M.create_anomaly_detector(
        AnomalyDetectorName=project_name + "-detector-" + str(uuid.uuid1()),
        AnomalyDetectorDescription="Text insights anomaly detector",
        AnomalyDetectorConfig={
            "AnomalyDetectorFrequency": frequency,
        },
    )

    logger.info(response_create)

    return response_create


def define_dataset(detector_arn, project_name, frequency, athena_role_arn, athena_config):
    params = {
        "AnomalyDetectorArn": detector_arn,
        "MetricSetName": project_name + '-metric-set-1',
        "MetricList": [
            {
                "MetricName": "count",
                "AggregationFunction": "AVG",
            }
        ],

        "DimensionList": ["platform", "category_type", "sentiment"],
        "Offset": 60,

        "TimestampColumn": {
            "ColumnName": "partition_timestamp",
            "ColumnFormat": "yyyy-MM-dd HH:mm:ss",
        },

        # "Delay" : 120, # seconds the detector will wait before attempting to read latest data per current time and detection frequency below
        "MetricSetFrequency": frequency,

        "MetricSource": {
            "AthenaSourceConfig": {
                "RoleArn": athena_role_arn,
                "DatabaseName": athena_config['db_name'],
                "DataCatalog": athena_config['data_catalog'],
                "TableName": athena_config['table_name'],
                "WorkGroupName": athena_config['workgroup_name'],
            }
        },
    }

    return params


@helper.create
@helper.update
def create(event, context):
    logger.info(event)

    cfn_input = event["ResourceProperties"]
    target = cfn_input["Target"]

    try:

        athena_role_arn = target['AthenaRoleArn']
        athena_config = {
            'db_name': target['GlueDbName'],
            'data_catalog': target['AwsDataCatalog'],
            'table_name': target['GlueTableName'],
            'workgroup_name': target['AthenaWorkgroupName']
        }
        sns_role_arn = target['SnsRoleArn']
        topic_arn = target['SnsTopicArn']
        alert_threshold = target['AlertThreshold']

        project = 'ai-powered-text-insights'
        frequency = target['DetectorFrequency']

        l4m_detector = create_detector(project, frequency)

        anomaly_detector_arn = l4m_detector["AnomalyDetectorArn"]
        dataset = define_dataset(anomaly_detector_arn, project, frequency, athena_role_arn, athena_config)

        L4M.create_metric_set(**dataset)

        """
        L4M.activate_anomaly_detector(AnomalyDetectorArn=anomaly_detector_arn)

        L4M.create_alert(
            Action={
                "SNSConfiguration": {
                    "RoleArn": sns_role_arn,
                    "SnsTopicArn": topic_arn
                }
            },
            AlertDescription="Text insights alert",
            AlertName=project + "-alert-all",
            AnomalyDetectorArn=anomaly_detector_arn,
            AlertSensitivityThreshold=int(alert_threshold)
        )
        """

        cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Data': 'Created L4M resource'}, anomaly_detector_arn)

    except Exception as e:

        logger.error(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {'Data': 'Failed to create L4M resource'}, '')


@helper.delete
def delete(event, _):
    logger.info(event)


def handler(_event, _context):
    helper(_event, _context)
