import json
import os
import pytest
import boto3
from moto import mock_aws

# Set ALL env vars before any import of lambda_function
os.environ['TABLE_NAME'] = 'PlayerStats'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture(autouse=True)
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='PlayerStats',
            KeySchema=[{'AttributeName': 'playerId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'playerId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.meta.client.get_waiter('table_exists').wait(
            TableName='PlayerStats'
        )
        yield table


def test_create_player_success(dynamodb_table):
    with mock_aws():
        import importlib
        import lambda_function
        importlib.reload(lambda_function)

        event = {
            'httpMethod': 'POST',
            'path': '/players',
            'body': json.dumps({
                'playerId': 'p001',
                'name': 'Abdulrahman',
                'team': 'Alpha'
            })
        }
        result = lambda_function.lambda_handler(event, {})
        assert result['statusCode'] == 201
        body = json.loads(result['body'])
        assert body['playerId'] == 'p001'
        assert 'createdAt' in body


def test_create_player_missing_fields(dynamodb_table):
    with mock_aws():
        import importlib, lambda_function
        importlib.reload(lambda_function)
        event = {
            'httpMethod': 'POST',
            'path': '/players',
            'body': json.dumps({'team': 'Alpha'})
        }
        result = lambda_function.lambda_handler(event, {})
        assert result['statusCode'] == 400


def test_get_player_not_found(dynamodb_table):
    with mock_aws():
        import importlib, lambda_function
        importlib.reload(lambda_function)
        event = {
            'httpMethod': 'GET',
            'path': '/players/ghost',
            'pathParameters': {'playerId': 'ghost'}
        }
        result = lambda_function.lambda_handler(event, {})
        assert result['statusCode'] == 404


def test_unknown_route(dynamodb_table):
    with mock_aws():
        import importlib, lambda_function
        importlib.reload(lambda_function)
        event = {'httpMethod': 'DELETE', 'path': '/unknown'}
        result = lambda_function.lambda_handler(event, {})
        assert result['statusCode'] == 404
