import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')

    if http_method == 'POST' and path == '/players':
        body = json.loads(event.get('body', '{}'))
        return create_player(body)
    elif http_method == 'GET' and '/players/' in path:
        player_id = event.get('pathParameters', {}).get('playerId', '')
        return get_player(player_id)

    return build_response(404, {'error': 'Route not found'})

def create_player(data):
    if not data.get('playerId') or not data.get('name'):
        return build_response(400, {'error': 'playerId and name required'})
    item = {
        'playerId': data['playerId'],
        'name': data['name'],
        'team': data.get('team', 'Unassigned'),
        'createdAt': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return build_response(201, item)

def get_player(player_id):
    if not player_id:
        return build_response(400, {'error': 'playerId required'})
    result = table.get_item(Key={'playerId': player_id})
    if 'Item' not in result:
        return build_response(404, {'error': f'Player {player_id} not found'})
    return build_response(200, result['Item'])

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
