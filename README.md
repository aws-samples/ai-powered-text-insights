# AI Powered Text Insights

# Table of Content

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Deployment](#deployment)
    - [Prerequisites](#prerequisites)
    - [Backend resources](#backend-resources)
    - [Test the application by streaming sample X.com posts](#optional-test-the-application-by-streaming-sample-xcom-posts)
    - [Stream real X.com posts to the application](#optional-test-the-application-by-streaming-sample-xcom-posts)
4. [Cost](#cost)
    - [Optional Costs](#optional-costs)
5. [Visualize your insights with Amazon QuickSight](#visualize-your-insights-with-amazon-quicksight)
6. [Cleanup](#clean-up)
7. [CDK Notes](#cdk-notes)
8. [Useful commands](#useful-commands)
9. [License](#license)

## Overview

This package includes the code of a prototype to help you gain insights on how your customers interact with you or your brand on social media. By leveraging Large Language Models (LLMs) on Amazon Bedrock we are able to extract real time insights (like topic, entities, sentiment, and more) from short text of any kind of short text (including posts on social media). We then use these insights to create rich visualizations on Amazon Quicksight and configure automated alerts using Amazon Lookout for Metrics. The solution consists of a text processing pipeline (using AWS Lambda) that extracts the following insights from posts on social media:

- Topic of the post
- Sentiment of the post
- Entities involved in the post
- Location of the post (if present)
- Links in the post (if present)
- Keyphrases in the post

This extraction is made by leveraging an LLM (Claude 3 Haiku) to extract such information and store it in a JSON object as described bellow 

```json
{
  "type": "object",
  "properties": {
    "topic": {
    "description": "the main topic of the post",
    "type": "string",
    "default": ""
    },
    "location": {
    "description": "the location, if exists, where the events occur",
    "type": "string",
    "default": ""
    },
    "entities": {
    "description": "the entities involved in the post",
    "type": "list",
    "default": []
    },
    "keyphrases": {
    "description": "the keyphrases in the post",
    "type": "list",
    "default": []
    },
    "sentiment": {
    "description": "the sentiment of the post",
    "type": "string",
    "default": ""
    },
    "links": {
    "description": "any links found withing the post",
    "type": "list",
    "default": []
    }
  }
}

```

If a processed text contains a location the coordinates of such location are obtained using Amazon Location Services. Processed posts are stored in an Amazon S3 bucket. Data stored in S3 is queried using Amazon Athena. Anomaly detection is performed on the volume of posts per category per period of time using Amazon Lookout for Metrics and notifications are sent when anomalies are detected. All insights can be presented in a QuickSight dashboard.

The application includes the following resources (directories): 

- `backend`: Contains all the code for the application and the deployment of the resources described in the Architecture diagram
- `data-streamer`: A sample application that streams sample X.com posts about New Year's resolutions to the AI Powered Text insights application
- `stream-getter`: A sample application to receive posts from a real X.com account to the AI Powered Text insights application
- `sample-files`: Example JSON objects of processed posts.


## Architecture

Deploying the sample application builds the following environment in the AWS Cloud:

![architecture](architecture.png)

1. An [Amazon Elastic Container Service](https://aws.amazon.com/ecs/) (Amazon ECS) task runs on serverless infrastructure managed by [AWS Fargate](https://aws.amazon.com/fargate/) and maintains an open connection to the social media.
2. The social media access tokens are securely stored in [AWS Systems Manager Parameter Store](https://aws.amazon.com/systems-manager/), and the container image is hosted on [Amazon Elastic Container Registry](https://aws.amazon.com/ecr/) (Amazon ECR).
3. When a new post arrives, it’s placed into an [Amazon Simple Queue Service](https://aws.amazon.com/sqs/) (SQS) queue.
4. The logic of the solution resides in [AWS Lambda](https://aws.amazon.com/lambda/) function microservices, coordinated by [AWS Step Functions](https://aws.amazon.com/step-functions/).
5. The post is processed in real time by one of the Large Language Models (LLM) supported by [Amazon Bedrock](https://aws.amazon.com/bedrock).
6. [Amazon Location Service](https://aws.amazon.com/location/) transforms a location name into coordinates. 
7. The post and metadata (insights) are sent to [Amazon Simple Storage Service](https://aws.amazon.com/s3/) (Amazon S3), and [Amazon Athena](https://aws.amazon.com/athena/) queries the processed tweets with standard SQL.
8. [Amazon Lookout for Metrics](https://aws.amazon.com/lookout-for-metrics/) looks for anomalies in the volume of mentions per category. [Amazon Simple Notification Service](https://aws.amazon.com/sns/) (Amazon SNS) sends an alert to users when an anomaly is detected.
9. We recommend setting up a [Amazon QuickSight](https://aws.amazon.com/quicksight/) Dashboard so that business users can easily visualize insights.

## Deployment

### Prerequisites

* AWS CLI. Refer to [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
* AWS Credentials configured in your environment. Refer to
  [Configuration and credential file settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
* AWS SAM CLI. Refer
  to [Installing the AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* AWS Copilot CLI. Refer to
  [Install Copilot](https://aws.github.io/copilot-cli/docs/getting-started/install/)
* Docker. Refer to [Docker](https://www.docker.com/products/docker-desktop)
* Get access to Claude 3 Haiku model on Amazon Bedrock. Follow the instructions in the [model access guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).
* Authenticate to Amazon ECR public registry. Follow this [guide to authenticate](https://docs.aws.amazon.com/AmazonECR/latest/public/public-registries.html)
* [Optional] Twitter application Bearer token. Refer
  to [OAuth 2.0 Bearer Token - Prerequisites](https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens)
* [Optional] Twitter Filtered stream rules configured. Refer to the examples in the end of this document and to
  [Building rules for filtered stream](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule)

### Backend resources

Run the command below, from within the `backend/` directory, to deploy the backend:

```
sam build --use-container && sam deploy --guided
```

Follow the prompts. NOTE: Due to a constraint in Lookout for Metrics naming of databases please name you stack using the following regular expression pattern: [a-zA-Z0-9_]+

The command above deploys an AWS CloudFormation stack in your AWS account. You will need the stack's output values to deploy
the Twitter stream getter container.

#### 1. Data format

This solution generates the posts insights, stored as JSON files, into four S3 locations, **/posts**, **/links**, **/topics**, and **/phrases**, on the results bucket whose name is specified by the CloudFormation stack's outputs under "PostsBucketName". Under each subfolder data is organized by day following the **YYYY-MM-dd 00:00:00** datetime format.

Sample output files can be found in this repository under the **/sample_files** folder. 

#### 2. Activate the Lookout for Metrics detector

To allow for you to provide historical data to the anomaly detector to [reduce the detector’s learning time](https://docs.aws.amazon.com/lookoutmetrics/latest/dev/services-athena.html) the prototype is deployed with the anomaly detector disabled.

If you have historical data with the same format as the data generated by this solution you may move it to the data S3 bucket generated by deploying the backend (PostsBucketName). Make sure to follow the format of the files in the **/sample_files** folder.

[Follow the instructions](https://docs.aws.amazon.com/lookoutmetrics/latest/dev/gettingstarted-detector.html) to activate your detector, the detector’s name can be found as part of the CloudFormation stack’s outputs.

Optionally you can configure alerts for your anomaly detector. [Follow the instructions](https://docs.aws.amazon.com/lookoutmetrics/latest/dev/gettingstarted-detector.html) to create an alert that sends a notification to SNS, the SNS topic name are part of the CloudFormation stack’s outputs.

### (Optional) Test the application by streaming sample X.com posts

This section is entirely optional. It will show you how to stream sample X.com posts to the Amazon SQS queue (2 in the architecture diagram) locally from your computer.

Navigate to ``data-streamer`` folder and run: 

```
python stream_posts.py \
--queue_url <SQS_QUEUE_URL> \
--region <DEPLOYMENT_REGION>
```

### (Optional) Stream real X.com posts to the application

This section is entirely optional. It will show you how to deploy the assets under **stream-getter** folder which creates an application (1 in the architecture diagram) to get X.com posts using the [streaming API](https://developer.twitter.com/en/docs/tutorials/stream-tweets-in-real-time).

Run the command below, from within the `stream-getter/` directory, to deploy the container application:

##### 1. Create application

```
copilot app init twitter-app
```

#### 2. Create environment

```
copilot env init --name test --region <BACKEND_STACK_REGION>
```

Replace `<BACKEND_STACK_REGION>` with the same region to which you deployed the backend resources previously.

Follow the prompts accepting the default values.

The above command provisions the required network infrastructure (VPC, subnets, security groups, and more). In its
default configuration, Copilot
follows [AWS best practices](https://aws.amazon.com/blogs/containers/amazon-ecs-availability-best-practices/) and
creates a VPC with two public and two private subnets in different Availability Zones (AZs). For security reasons, we'll
soon configure the placement of the service as _private_. Because of that, the service will run on the private subnets
and Copilot will automatically add NAT Gateways, but NAT Gateways increase the overall cost. In case you decide to run
the application in a single AZ to have only one NAT Gateway **(not recommended)**, you can run the following command
instead:

```
copilot env init --name test --region <BACKEND_STACK_REGION> \
    --override-vpc-cidr 10.0.0.0/16 --override-public- cidrs 10.0.0.0/24 --override-private-cidrs 10.0.1.0/24
```

**Note:** The current implementation is prepared to run one container at a time solely. Not only your Twitter account
should allow you to have more than one Twitter's stream connection at a time, but the application also must be modified
to handle other complexities such as duplicates (learn more
in [Recovery and redundancy features](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/recovery-and-redundancy-features)).
Even though there will be only one container running at a time, having two AZs is still recommended, because in case
one AZ is down, ECS can run the application in the other AZ.

#### 3. Deploy the environment

```
copilot env deploy --name test
```

#### 4. Create service

```
copilot svc init --name stream-getter --svc-type "Backend Service" --dockerfile ./Dockerfile
```

#### 5. Create secret to store the Twitter Bearer token

```
copilot secret init --name TwitterBearerToken
```

When prompted to provide the secret, paste the Twitter Bearer token.

#### 6. Edit service manifest

Open the file `copilot/stream-getter/manifest.yml` and change its content to the following:

```
name: stream-getter
type: Backend Service

image:
  build: Dockerfile

cpu: 256
memory: 512
count: 1
exec: true

network:
  vpc:
    placement: private

variables:
  SQS_QUEUE_URL: <SQS_QUEUE_URL>
  LOG_LEVEL: info

secrets:
  BEARER_TOKEN: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/TwitterBearerToken
```

Replace `<SQS_QUEUE_URL>` with the URL of the SQS queue deployed in your AWS account.

You can use the following command to get the value from the backend AWS CloudFormation stack outputs
(replace `<BACKEND_STACK_NAME>` with the name of your backend stack):

```
aws cloudformation describe-stacks --stack-name <BACKEND_STACK_NAME> \
    --query "Stacks[].Outputs[?OutputKey=='TweetsQueueUrl'][] | [0].OutputValue"
```

#### 7. Add permission to write to the queue

Create a new file in `copilot/stream-getter/addons/` called `sqs-policy.yaml` with the following content:

```
Parameters:
  App:
    Type: String
    Description: Your application's name.
  Env:
    Type: String
    Description: The environment name your service, job, or workflow is being deployed to.
  Name:
    Type: String
    Description: The name of the service, job, or workflow being deployed.

Resources:
  QueuePolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Sid: SqsActions
            Effect: Allow
            Action:
              - sqs:SendMessage
            Resource: <SQS_QUEUE_ARN>

Outputs:
  QueuePolicyArn:
    Description: The ARN of the ManagedPolicy to attach to the task role.
    Value: !Ref QueuePolicy

```

Replace `<SQS_QUEUE_ARN>` with the ARN of the SQS queue deployed in your AWS account.

You can use the following command to get the value from the backend AWS CloudFormation stack outputs
(replace `<BACKEND_STACK_NAME>` with the name of your backend stack):

```
aws cloudformation describe-stacks --stack-name <BACKEND_STACK_NAME> \
    --query "Stacks[].Outputs[?OutputKey=='TweetsQueueArn'][] | [0].OutputValue"
```

After that, your directory should look like the following:

```
.
├── Dockerfile
├── backoff.py
├── copilot
│     ├── stream-getter
│     │    ├── addons
│     │    │     └── sqs-policy.yaml
│     │    └── manifest.yml
│     └── environments
│          └── test
│               └── manifest.yml
├── main.py
├── requirements.txt
├── sqs_helper.py
└── stream_match.py
```

#### 8. Deploy service

> **IMPORTANT:** The container will connect to the Twitter stream as soon as it starts, after deploying the service. You need your Twitter stream rules configured before connecting to the stream. Therefore, if you haven't configured the rules yet, configure them before proceeding.

```
copilot svc deploy --name stream-getter --env test
```

When the deployment finishes, you should have the container running inside ECS. To check the logs, run the following:

```
copilot svc logs --follow
```

#### 9. Rules examples for filtered stream

Twitter provides endpoints that enable you to create and manage rules, and apply those rules to filter a stream of
real-time tweets that will return matching public tweets.

For instance, following is a rule that returns tweets from the accounts `@awscloud`, `@AWSSecurityInfo`, and `@AmazonScience`:

```
from:awscloud OR from:AWSSecurityInfo OR from:AmazonScience
```

To add that rule, issue a request like the following, replacing `<BEARER_TOKEN>` with the Twitter Bearer token:

```
curl -X POST 'https://api.twitter.com/2/tweets/search/stream/rules' \
-H "Content-type: application/json" \
-H "Authorization: Bearer <BEARER_TOKEN>" -d \
'{
  "add": [
    {
      "value": "from:awscloud OR from:AWSSecurityInfo OR from:AmazonScience",
      "tag": "news"
    }
  ]
}'
```

## Cost

You are responsible for the cost of the AWS services used while running this Guidance. 

As of May 2024, the cost for running this Guidance continuously for one month, with the default settings in the US East (N.Virginia) Region, and processing 1000 posts a day is approximately $150 per month.

After the stack is destroyed, you will stop incurring in costs.

The table below shows the resources provisioned by this CDK stack, and their respective cost. The table below does not consider free tier.

|Resource|Description|Approximate Cost|
|--------|-----------|----------|
| AWS Lambda | Functions for processing the text | 2 USD |
| Amazon Simple Queue Service | Queue to get text to process | 1 USD |
| Amazon Location Service	 | Pinpoint the locations mentioned in the text | 15 USD |
| Amazon Simple Storage Service | Store the processed short text | 1 USD |
| Amazon Athena | Query processed text and its metadata | 49 USD |
| Amazon QuickSight | Visualize the processed text and metadata | 23 USD |
| Amazon Lookout for Metrics | Detect anomalies in the trends mentiond in the text | 7 USD |
| AWS Step Functions | Manage the text processing pipeline | 4 USD |
| Amazon Bedrock (Claude 3 Haiku) | Extract information from the text | 45 USD |
| Total |  | 147 USD |

### Optional costs

The following costs will only be incurred if you deploy the resources in the Optional section [Stream real X.com posts to the application](#optional-stream-real-xcom-posts-to-the-application)

|Resource|Description|Approximate Cost|
|--------|-----------|----------|
| AWS Fargate | Run the ECR container serverless | 37 USD |
| Total |  | 37 USD |

## Visualize your insights with Amazon QuickSight

To create some example visualizations from the processed text data follow the instructions on the [Creating visualizations with QuickSight.pdf](Creating_visualizations_with_QuickSight.pdf) file.

## Clean up

If you don't want to continue using the sample, clean up its resources to avoid further charges.

Start by deleting the backend AWS CloudFormation stack which, in turn, will remove the underlying resources created then delete all the resources AWS Copilot set up for the container application, run the following commands:

```
sam delete --stack-name <sam stack name>
```

Additionally, if you deployed the X.com streaming application delete the deployed resources with:

```
copilot svc delete --name stream-getter
copilot env delete --name test
copilot app delete
```

## CDK Notes:

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.