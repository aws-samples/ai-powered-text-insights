# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3

L4M = boto3.client("lookoutmetrics")

def create_detector(project_name, frequency):

    try:

        response = L4M.create_anomaly_detector(
            AnomalyDetectorName=project_name + "-detector",
            AnomalyDetectorDescription="Twister DC Anomaly detector",
            AnomalyDetectorConfig={
                "AnomalyDetectorFrequency": frequency,
            },
        )

    except Exception as e:
        print(e)

    return response


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
                "WorkGroupName": athena_config['work_group_name'],

            }
        },
    }

    return params


if __name__ == '__main__':

    athena_role_arn = 'arn:aws:iam::417308874955:role/text-classification-backend-AthenaSourceAccessRole-5WFMMW0EG61C'
    athena_config = {
        'db_name': 'tweets',
        'data_catalog': 'AwsDataCatalog',
        'table_name': 'tweets',
        'workgroup_name': 'TweetsWorkGroup'
    }
    sns_role_arn = ''
    topic_arn = 'arn:aws:sns:us-east-1:417308874955:text-classification-backend-AlertTopic-4NNI4O0RSVSZ'

    project = 'twister-dc'
    frequency = 'PT1H'

    l4m_detector = create_detector(project, frequency)

    anomaly_detector_arn = l4m_detector["AnomalyDetectorArn"]
    dataset = define_dataset(anomaly_detector_arn, project, frequency, athena_role_arn, athena_config)

    L4M.create_metric_set(**dataset)
    L4M.activate_anomaly_detector(AnomalyDetectorArn=anomaly_detector_arn)

    response = L4M.create_alert(
        Action={
            "SNSConfiguration": {
                "RoleArn": sns_role_arn,
                "SnsTopicArn": topic_arn
            }
        },
        AlertDescription="Twister DC Alert",
        AlertName=project + "-alert-all",
        AnomalyDetectorArn=anomaly_detector_arn,
        AlertSensitivityThreshold=50
    )


