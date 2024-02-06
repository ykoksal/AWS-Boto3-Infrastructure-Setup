import config

public_ec2_id = config.public_ec2_id
private_ec2_id = config.private_ec2_id
public_instance = config.public_instance
private_instance = config.private_instance

#Start Instances
resp_start_public_instance = public_instance.start()
resp_start_private_instance = private_instance.start()
public_start_code = resp_start_public_instance['ResponseMetadata']['HTTPStatusCode']
private_start_code = resp_start_private_instance['ResponseMetadata']['HTTPStatusCode']
print(f'Start HTTP Responses\nPrivate Instance: {private_start_code}, Public Instance: {public_start_code})')

#Stop Instances
resp_stop_public_instance = public_instance.stop()
resp_stop_private_instance = private_instance.stop()
public_stop_code = resp_stop_public_instance['ResponseMetadata']['HTTPStatusCode']
private_stop_code = resp_stop_private_instance['ResponseMetadata']['HTTPStatusCode']
print(f'Stop HTTP Responses\nPrivate Instance: {private_stop_code},\nPublic Instance: {public_stop_code})')

#Terminate Instances
resp_terminate_public_instance = public_instance.terminate()
resp_terminate_private_instance = private_instance.terminate()
public_terminate_code = resp_terminate_public_instance['ResponseMetadata']['HTTPStatusCode']
private_terminate_code = resp_terminate_private_instance['ResponseMetadata']['HTTPStatusCode']
print(f'terminate HTTP Responses\nPrivate Instance: {private_terminate_code},\nPublic Instance: {public_terminate_code})')