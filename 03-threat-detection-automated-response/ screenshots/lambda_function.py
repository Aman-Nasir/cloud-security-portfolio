import boto3
import json

iam = boto3.client('iam')
sns = boto3.client('sns')

SNS_TOPIC_ARN = "arn:aws:sns:ap-southeast-2:201409139831:guardduty-alerts"

def lambda_handler(event, context):
    print("Received GuardDuty finding:", json.dumps(event))
    
    detail = event.get('detail', {})
    finding_type = detail.get('type', 'Unknown')
    severity = detail.get('severity', 0)
    
    access_key_details = detail.get('resource', {}).get('accessKeyDetails', {})
    user_name = access_key_details.get('userName')
    
    action_taken = "No action (informational finding, no IAM user found)"
    
    if user_name:
        try:
            keys = iam.list_access_keys(UserName=user_name)
            for key in keys['AccessKeyMetadata']:
                iam.update_access_key(
                    UserName=user_name,
                    AccessKeyId=key['AccessKeyId'],
                    Status='Inactive'
                )
            action_taken = f"Deactivated access keys for user: {user_name}"
        except Exception as e:
            action_taken = f"Error handling user {user_name}: {str(e)}"
    
    message = (
        f"GuardDuty Finding Detected!\n"
        f"Type: {finding_type}\n"
        f"Severity: {severity}\n"
        f"Action Taken: {action_taken}"
    )
    
    if SNS_TOPIC_ARN != "PASTE_YOUR_SNS_TOPIC_ARN_HERE":
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🚨 GuardDuty Auto-Response Alert",
            Message=message
        )
    
    print(message)
    return {
        'statusCode': 200,
        'body': message
    }
