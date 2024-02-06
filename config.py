#Config
public_ec2_id = public_ec2_instance[0].id
private_ec2_id = private_ec2_instance[0].id
public_instance = ec2.Instance(public_ec2_id)
private_instance = ec2.Instance(private_ec2_id)