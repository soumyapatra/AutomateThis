import boto3
import logging

inst_id = 'i-008e9a3670bcda419'
ssm = boto3.client('ssm')
response = ssm.send_command(InstanceIds=[inst_id], DocumentName='InstallCwAgent', TimeoutSeconds=600)
print(response)

command_id = response['Command']['CommandId']
# get_comm_inv=ssm.get_command_invocation(InstanceId='i-008e9a3670bcda419',CommandId=command_id)
# print("GET_COMM_INV",get_comm_inv)

list_comm_inv = ssm.list_command_invocations(CommandId=command_id, InstanceId='i-008e9a3670bcda419')
print("LIST_COMM_INV", list_comm_inv)
