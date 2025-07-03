import json
import os
import time
import traceback
from lb_ops import *
from alarms import *
from ec2_ops import *
from sns_ops import pub_sns
from slack_ops import slack_send

REGION = os.environ['REGION']
ENV = os.environ['ENV']
SNS_ARN = os.environ['SNS_ARN']
ALERT_SNS_ARN = os.environ['ALERT_SNS_ARN']


def lambda_handler(event, context):
    # TODO implement
    body = event["Records"][0]["body"]
    if event["Records"][0]["attributes"]["MessageGroupId"] == "lb_group":
        json_body = json.loads(body)
        print(json.dumps(json_body))

        try:
            if "errorCode" in json_body["detail"]:
                func_name = context.function_name
                evnt_id = json_body['id']
                acct = json_body["account"]
                details = json_body['detail']['errorMessage']
                msg = f'Error in {func_name}\n===================\nID: {evnt_id}\nAcct: {acct}\nDetails: {details}'
                sub = f'Error in {func_name}'
                slack_send('slack_integration_testing', msg, sub)
                return
            print(json.dumps(json_body))
            detail = json_body['detail']
            if "state" in detail:
                if detail['state'] == "stopped":
                    instance_id = detail['instance-id']
                    delCwAlarm(instance_id)
                    return
            eventname = detail['eventName']
            print(f'Event Name:', eventname)
            response = detail['responseElements']
            if eventname == "StartInstances":
                instance_sets = response['instancesSet']['items']
                for item in instance_sets:
                    if item['previousState']['name'] == "stopped" and item['currentState']['name'] == "pending":
                        instance_id = item['instanceId']
                        print(instance_id)

                        name = get_inst_tag(instance_id, "Name")

                        if name == "Packer Builder" or name == "mab_emr" or name == "mab_presto_cluster":
                            print("Packer/EMR instance. Ignoring !!!")
                            continue

                        jenkins_tag = get_inst_tag(instance_id, "iam_identifier_tag")

                        if jenkins_tag == "jenkins_worker":
                            print("jenkins Instance. Ignoring !!!")
                            continue

                        if check_bi_tag(instance_id):
                            print(put_cpu_alarm(instance_id, ENV, SNS_ARN, name))
                            print(put_mem_alarm(instance_id, ENV, SNS_ARN, name))
                            print(put_instance_status_check(instance_id, ENV, SNS_ARN, name))
                            print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
                            try:
                                print(put_autorecovery_check_recover_action(instance_id, ENV, SNS_ARN, name))
                            except ClientError:
                                print("instance not supported. creating normal autorecover alarm")
                                print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
                        else:
                            print(put_cpu_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                            print(put_mem_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                            print(put_instance_status_check(instance_id, ENV, ALERT_SNS_ARN, name))
                            print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
                            try:
                                print(put_autorecovery_check_recover_action(instance_id, ENV, ALERT_SNS_ARN, name))
                            except ClientError:
                                print("instance not supported. creating normal autorecover alarm")
                                print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
            elif eventname == "StopInstances":
                instance_sets = response['instancesSet']['items']
                print(eventname)
                for item in instance_sets:
                    if item['previousState']['name'] == "running" and item['currentState']['name'] == "stopping":
                        instance_id = item['instanceId']
                        delCwAlarm(instance_id)
            elif eventname == "TerminateInstances":
                instance_sets = response['instancesSet']['items']
                for item in instance_sets:
                    instance_id = item['instanceId']
                    delCwAlarm(instance_id)
            elif eventname == "RunInstances":
                time.sleep(30)
                instance_sets = response['instancesSet']['items']
                for item in instance_sets:
                    monitor_state = item['monitoring']['state']
                    instance_id = item['instanceId']
                    if monitor_state == "disabled":
                        print(f'Enabling Deailed Monitor for instance {instance_id}')
                        # enable_detailed_monitor(instance_id)

                    name = get_inst_tag(instance_id, "Name")
                    if name == "Packer Builder" or name == "mab_emr" or name == "mab_presto_cluster":
                        print("Packer/EMR instance. Ignoring !!!")
                        continue

                    jenkins_tag = get_inst_tag(instance_id, "iam_identifier_tag")

                    if jenkins_tag == "jenkins_worker":
                        print("jenkins Instance. Ignoring !!!")
                        continue

                    if name == "Packer Builder":
                        print("Packer Instance. Ignoring !!!")
                        return
                    if check_bi_tag(instance_id):
                        print(put_cpu_alarm(instance_id, ENV, SNS_ARN, name))
                        print(put_mem_alarm(instance_id, ENV, SNS_ARN, name))
                        print(put_instance_status_check(instance_id, ENV, SNS_ARN, name))
                        print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
                        try:
                            print(put_autorecovery_check_recover_action(instance_id, ENV, SNS_ARN, name))
                        except ClientError:
                            print("instance not supported. creating normal autorecover alarm")
                            print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
                    else:
                        print(put_cpu_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                        print(put_mem_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                        print(put_instance_status_check(instance_id, ENV, ALERT_SNS_ARN, name))
                        print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
                        try:
                            print(put_autorecovery_check_recover_action(instance_id, ENV, ALERT_SNS_ARN, name))
                        except ClientError:
                            print("instance not supported. creating normal autorecover alarm")
                            print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
            elif eventname == "CreateLoadBalancer":
                time.sleep(300)
                if "loadBalancers" in response:
                    for lb in response['loadBalancers']:
                        if "type" in lb:
                            if lb["type"] == "network":
                                lb_arn_raw = lb["loadBalancerArn"]
                                print("CREATING NLB ALARMS: ", lb_arn_raw)
                                nlb_info = get_alb_info(lb_arn_raw)
                                tag = nlb_info['tag']
                                nlb_name = nlb_info['alb_name']
                                nlb_arn = nlb_info['alb_arn']
                                scheme = nlb_info['scheme']
                                name = f'{tag}:{nlb_name}:{scheme}'
                                if get_trgt_arn(lb_arn_raw):
                                    tgs = get_trgt_arn(lb_arn_raw)
                                    for tg in tgs:
                                        tg_name = tg.split('/')[1]
                                        name_with_tg = f'{tag}:{nlb_name}:{tg_name}:{scheme}'
                                        put_nlb_unhealthyhost(name_with_tg, nlb_arn, tg, ALERT_SNS_ARN)
                                put_nlb_client_reset(name, nlb_arn, ALERT_SNS_ARN)
                                put_nlb_elb_reset(name, nlb_arn, ALERT_SNS_ARN)
                                put_nlb_target_reset(name, nlb_arn, ALERT_SNS_ARN)
                                put_nlb_tls_error(name, nlb_arn, ALERT_SNS_ARN)
                            elif lb["type"] == "application":
                                print("CREATING ALB ALARMS")
                                alb_arn_raw = lb["loadBalancerArn"]
                                print("ALB ARN: ", alb_arn_raw)
                                alb_info = get_alb_info(alb_arn_raw)
                                print(alb_info)
                                tag = alb_info['tag']
                                alb_name = alb_info['alb_name']
                                alb_arn = alb_info['alb_arn']
                                scheme = alb_info['scheme']
                                name = f'{tag}:{alb_name}:{scheme}'
                                if get_trgt_arn(alb_arn_raw):
                                    tgs = get_trgt_arn(alb_arn_raw)
                                    for tg in tgs:
                                        tg_name = tg.split('/')[1]
                                        name_with_tg = f'{tag}:{alb_name}:{tg_name}:{scheme}'
                                        put_alb_unhealthyhost(name_with_tg, alb_arn, tg, ALERT_SNS_ARN)
                                        put_target_resp_alb_alarm(name_with_tg, alb_arn, tg, ALERT_SNS_ARN)
                                        put_5xx_alb_target_alarm(name_with_tg, tg, alb_arn, ALERT_SNS_ARN)
                                        put_4xx_alb_alarm(name_with_tg, tg, alb_arn, ALERT_SNS_ARN)
                                    put_5xx_alb_alarm(name, alb_arn, ALERT_SNS_ARN)
                else:
                    lb_name = detail["requestParameters"]["loadBalancerName"]
                    print("CREATING ELB ALARMS")
                    print(lb_name)
                    elb_info = get_elb_info(lb_name)
                    tag = elb_info['tag']
                    scheme = elb_info['scheme']
                    name = f'{tag}:{lb_name}:{scheme}'
                    put_elb_unhealthy(name, lb_name, ALERT_SNS_ARN)
                    put_elb_backend_5xx(name, lb_name, ALERT_SNS_ARN)
                    put_elb_latency(name, lb_name, ALERT_SNS_ARN)
                    put_elb_5xx(name, lb_name, ALERT_SNS_ARN)
            elif eventname == "DeleteLoadBalancer":
                if "loadBalancerName" in detail["requestParameters"]:
                    lb_name = detail["requestParameters"]["loadBalancerName"]
                    alarm_names = get_alarm_names(lb_name, 'elb')
                    for alarm in alarm_names:
                        print(f'Deleting {alarm}')
                        print(cw.delete_alarms(AlarmNames=alarm_names))
                    msg = f'Following CW Alarm has been deleted for ELB {lb_name}:\n{alarm_names}'
                    sub = f'CloudWatch Alarm Deleted: {lb_name}'
                    print(pub_sns(SNS_ARN, msg, sub))

                elif "loadBalancerArn" in detail["requestParameters"]:
                    lb_arn = detail["requestParameters"]["loadBalancerArn"].split(':')[-1].replace('loadbalancer/', '')
                    print(lb_arn)
                    alarm_names = get_alarm_names(lb_arn, 'alb')
                    for alarm in alarm_names:
                        print(f'Deleting {alarm}')
                        print(cw.delete_alarms(AlarmNames=alarm_names))
                    msg = f'Following CW Alarm has been deleted for ALB {lb_arn}:\n{alarm_names}'
                    sub = f'CloudWatch Alarm Deleted: {lb_arn}'
                    print(pub_sns(SNS_ARN, msg, sub))
        except Exception as e:
            print("Issue occurred:", e)
            traceback.print_exc()
            message = f'Issue while creating/deleting alarm: {e}'
            pub_sns(ALERT_SNS_ARN, message, "Issue in CW Alarm Lambda")
