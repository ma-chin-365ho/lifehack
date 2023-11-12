import json
import datetime
import boto3
import os

EC2_OPERATING_MINUTE = int(os.environ["EC2_OPERATING_MINUTE"])
EC2_INSTANCE_ID = os.environ["EC2_INSTANCE_ID"]
EVENT_BRIDGE_SCHEDUAL_ROLE_ARN = os.environ["EVENT_BRIDGE_SCHEDUAL_ROLE_ARN"]

JST = datetime.timezone(datetime.timedelta(hours=9), 'JST')

client_ec2 = boto3.client('ec2')
client_sheduler = boto3.client('scheduler')

def lambda_handler(event, context):
    body = {}
    
    req_type = event["body"]["type"]
    
    # NOTE:起動停止繰り返すと課金されるため、即時停止は作らない。
    if req_type == "start":
        body = start_ec2(EC2_INSTANCE_ID, EC2_OPERATING_MINUTE)
    
    elif req_type == "info":
        body = get_ec2_info(EC2_INSTANCE_ID)
    
    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }
    
def start_ec2(instance_id, operating_minutes = None):
    """
    EC2 開始
    """

    # NOTE: 起動中に再実行してもException出ない。
    client_ec2.start_instances(
        InstanceIds=[
            instance_id,
        ],
    )
    
    if operating_minutes is not None:
        stop_ec2_schedual(instance_id, operating_minutes)
        
def stop_ec2_schedual(instance_id, operating_minutes):
    """
    Event Bridge Schedual 経由でEC2停止

    スケジュールの初回はすでに手動登録されている前提
    """
    stop_dt = datetime.datetime.now(JST).replace(tzinfo=None) + datetime.timedelta(minutes=operating_minutes)
    
    # NOTE:Targetの値を調べる時
    # print(client_sheduler.get_schedule(Name="test"))    
    client_sheduler.update_schedule(
        Name=f"stop-{instance_id}",
        State='ENABLED',
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },
        ScheduleExpression=f"at({stop_dt.isoformat(timespec='seconds')})",
        ScheduleExpressionTimezone="Asia/Tokyo",
        Target={
            'Arn': 'arn:aws:scheduler:::aws-sdk:ec2:stopInstances',
            'Input': '{\n  "InstanceIds": [\n    "' + instance_id + '"\n  ]\n}',
            'RetryPolicy': {
                'MaximumEventAgeInSeconds': 86400,
                'MaximumRetryAttempts': 185
            },
            'RoleArn': EVENT_BRIDGE_SCHEDUAL_ROLE_ARN
        }
    )
    
def get_ec2_info(instance_id):
    """
    EC2の情報取得
    """
    ec2_info_list = client_ec2.describe_instances(
        Filters=[{'Name':'instance-id', 'Values':[instance_id]}]
    )
    
    state = ""
    try:
        state = ec2_info_list['Reservations'][0]['Instances'][0]['State']['Name']
    except:
        pass
        
    ip = ""
    try:
        ip = ec2_info_list['Reservations'][0]['Instances'][0]['PublicIpAddress']
    except:
        pass

    return {
        "state" : state,
        "ip" : ip
    }
    