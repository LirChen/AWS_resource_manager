import json
import uuid

import click
import boto3
import os
import random
import string
from botocore.exceptions import ClientError
from tabulate import tabulate

OWNER = "lirchen"

@click.group()
def cli():
    pass

@cli.group()
def ec2():
    pass

@cli.group()
def s3():
    pass

@cli.group()
def route53():
    pass

def connect(service):
    AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_DEFAULT_REGION")
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    client = session.client(service)
    return client

@ec2.command("create")
@click.argument("ami", type=click.Choice(["ubuntu", "amazon-linux"], case_sensitive=False))
@click.argument("instance_type", type=click.Choice(["t3.micro", "t2.small"], case_sensitive=False))
def create_ec2(ami,instance_type):
    """
    AMI: ubuntu/amazon-linux

    instance_type: t3.micro/t2.small
    """
    client = connect("ec2")
    ami_options = {
        "ubuntu": "ami-020cba7c55df1f615",
        "amazon-linux": "ami-00ca32bbc84273381"
    }
    running_instances = instance_list_ec2()
    if running_instances < 2:
        response = client.run_instances(
            ImageId=ami_options[ami.lower()],
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": f"{OWNER}-{ami}-{instance_type}"},
                        {"Key": "CreatedBy", "Value": OWNER},
                    ]
                }
            ]
        )

        instance_id = response["Instances"][0]["InstanceId"]
        print(f"Instance created: {instance_id} ({ami}, {instance_type})")
    else:
        print("You can't have more than 2 running instances.")

@ec2.command("manage")
@click.argument("action", type=click.Choice(["start", "stop", "terminate"], case_sensitive=False))
@click.argument("instance")
def manage_ec2(action, instance):
    """
    action: start/stop/terminate

    instance: i-xxxxxxxxxx
    """
    client = connect("ec2")

    try:
        if action == "start":
            running_instances = instance_list_ec2()
            if running_instances < 2:
                client.start_instances(InstanceIds=[instance])
                print(f"Instance {instance} started.")
            else:
                print(f"You can't have more than 2 running instances.")
        elif action == "stop":
            client.stop_instances(InstanceIds=[instance])
            print(f"Instance {instance} stopped.")
        elif action == "terminate":
            client.terminate_instances(InstanceIds=[instance])
            print(f"Instance {instance} terminated.")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidInstanceID.NotFound':
            print(f"Instance '{instance}' does not exist")
        elif error_code == 'IncorrectInstanceState':
            print(f"Cannot {action} instance '{instance}' - incorrect state")
        elif error_code == 'UnauthorizedOperation':
            print(f"No permission to {action} instance '{instance}'")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def instance_list_ec2():
    """
    list all ec2 instances
    """
    client = connect("ec2")
    response = client.describe_instances(
        Filters=[
            {"Name": "tag:CreatedBy", "Values": [OWNER]}
        ]
    )
    exist = False
    count = 0

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append([
                instance["InstanceId"],
                next((tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "N/A"),
                instance["InstanceType"],
                instance["State"]["Name"]
            ])
            if instance["State"]["Name"] == "running":
                count += 1

    if not instances:
        print(f"No instances created by {OWNER}")
        return 0
    else:
        print(f"Instances created by {OWNER}:")
        print(tabulate(instances, headers=["ID", "Name", "Type", "State"], tablefmt="grid"))
        return count

@ec2.command("list")
def list_ec2():
    instance_list_ec2()

@s3.command("create")
@click.argument("visibility", type=click.Choice(["public", "private"], case_sensitive=False))
def create_s3(visibility):
    """
    visibility: public/private
    """
    if visibility.lower() == "public":
        if not click.confirm("Are you sure you want to make this bucket public?"):
            click.echo("Aborted.")
            return

    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    bucket_name = f"s3-bucket-{OWNER.lower()}-{random_id}"
    print(f"Creating bucket: {bucket_name}")

    try:
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket created: {bucket_name}")

        if visibility.lower() == "public":
            try:
                s3_client.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': False,
                        'IgnorePublicAcls': False,
                        'BlockPublicPolicy': False,
                        'RestrictPublicBuckets': False
                    }
                )

                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                }

                s3_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
                print("Bucket set to public using policy")

            except ClientError as e:
                print(f"Could not make bucket public: {e}")
                print("Bucket remains private for security.")
                visibility = "private"

        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {'Key': 'CreatedBy', 'Value': OWNER.lower()},
                    {'Key': 'Visibility', 'Value': visibility}
                ]
            }
        )
        print("Tags added")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            print(f"Bucket name '{bucket_name}' already exists globally")
        elif error_code == 'InvalidBucketName':
            print(f"Invalid bucket name '{bucket_name}'")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


@s3.command("delete")
@click.argument("bucket")
def delete_s3(bucket):
    """
    bucket: s3-bucket-lirchen-xxxxxx
    """
    try:
        s3_client = boto3.client('s3')

        try:
            tags_response = s3_client.get_bucket_tagging(Bucket=bucket)
            tags = {tag['Key']: tag['Value'] for tag in tags_response['TagSet']}

            if tags.get('CreatedBy') != OWNER.lower():
                print(f"Bucket '{bucket}' was not created by this CLI")
                print("You can only delete buckets created by platform-cli")
                return

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print(f"Bucket '{bucket}' does not exist")
                return
            elif error_code == 'NoSuchTagSet':
                print(f"Bucket '{bucket}' has no tags - not created by CLI")
                return
            else:
                print(f"Error checking bucket: {e}")
                return

        print(f"About to delete bucket: {bucket}")
        if not click.confirm(f"Are you sure you want to delete '{bucket}'?"):
            print("Aborted.")
            return

        try:
            objects_response = s3_client.list_objects_v2(Bucket=bucket)
            if 'Contents' in objects_response:
                objects_to_delete = [{'Key': obj['Key']} for obj in objects_response['Contents']]
                s3_client.delete_objects(
                    Bucket=bucket,
                    Delete={'Objects': objects_to_delete}
                )
                print(f"Deleted {len(objects_to_delete)} objects from bucket")
        except ClientError as e:
            print(f"Could not delete objects: {e}")

        s3_client.delete_bucket(Bucket=bucket)
        print(f"Bucket '{bucket}' deleted successfully")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketNotEmpty':
            print(f"Bucket '{bucket}' is not empty")
        elif error_code == 'NoSuchBucket':
            print(f"Bucket '{bucket}' does not exist")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@s3.command("upload")
@click.argument("file_path")
@click.argument("bucket_name")
@click.argument("object_name")
def upload_file_s3(file_path, bucket_name, object_name):
    """
    Uploads a specified local file to an AWS S3 bucket.

    local_file_path: The path to the local file to upload.

    bucket_name: The name of the S3 bucket.

    object_name: The name of the file to upload.
    """
    client = connect("s3")
    client.upload_file(file_path, bucket_name, object_name)
    print("The file was uploaded to S3 bucket successfully")

@s3.command("list")
def list_s3():
    """
    List all S3 buckets.
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.list_buckets()

        buckets = []
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            try:
                tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
                tags = {tag['Key']: tag['Value'] for tag in tags_response['TagSet']}

                if tags.get('CreatedBy') == OWNER.lower():
                    buckets.append([
                        bucket_name,
                        tags.get('Visibility', 'N/A'),
                        bucket['CreationDate'].strftime('%Y-%m-%d %H:%M'),
                        "CLI-created"
                    ])
            except ClientError:
                continue

        if not buckets:
            print(f"No S3 buckets created by {OWNER}")
        else:
            print(f"S3 buckets created by {OWNER}:")
            print(tabulate(buckets, headers=["Bucket Name", "Visibility", "Created", "Source"], tablefmt="grid"))

    except ClientError as e:
        print(f"Error listing buckets: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@route53.command("create")
@click.argument("domain_name")
def create_route53(domain_name):
    """
    domain_name: The domain name for the hosted zone (e.g., "example.com").
    """
    client = connect("route53")
    call_ref = str(uuid.uuid4())
    response = client.create_hosted_zone(Name=domain_name, CallerReference=call_ref)
    zone_id = response['HostedZone']['Id'].split('/')[-1]
    client.change_tags_for_resource(ResourceType="hostedzone", ResourceId=zone_id, AddTags=[{"Key": "CreatedBy", "Value": OWNER}])
    print(f"Created hosted zone {zone_id}")


@route53.command("delete")
@click.argument("zone_id")
def delete_route53(zone_id):
    """
    zone_id: The hosted zone ID to delete
    """
    try:
        client = connect("route53")

        try:
            zone_response = client.get_hosted_zone(Id=zone_id)
            zone_name = zone_response['HostedZone']['Name']

            tags_response = client.list_tags_for_resource(
                ResourceType="hostedzone",
                ResourceId=zone_id
            )
            tags = {tag['Key']: tag['Value'] for tag in tags_response['ResourceTagSet']['Tags']}

            if tags.get('CreatedBy') != OWNER:
                print(f"Hosted zone '{zone_id}' was not created by this CLI")
                return

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchHostedZone':
                print(f"Hosted zone '{zone_id}' does not exist")
                return
            else:
                print(f"Error checking zone: {e}")
                return

        print(f"About to delete hosted zone: {zone_name} ({zone_id})")
        if not click.confirm(f"Are you sure you want to delete zone '{zone_name}'?"):
            print("Aborted.")
            return

        client.delete_hosted_zone(Id=zone_id)
        print(f"Hosted zone '{zone_name}' ({zone_id}) deleted successfully")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchHostedZone':
            print(f"Hosted zone '{zone_id}' does not exist")
        elif error_code == 'HostedZoneNotEmpty':
            print(f"Cannot delete zone '{zone_id}' - it contains DNS records")
            print("Delete all custom DNS records first")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@route53.command("manage")
@click.argument("action", type=click.Choice(["create", "update", "delete"], case_sensitive=False))
@click.argument("zone_id")
@click.argument("record_name")
@click.argument("record_type")
@click.argument("record_value")
def manage_route53(action, zone_id, record_name, record_type, record_value):
    """
    action: create/update/delete

    zone_id: The ID of the hosted zone.

    record_name: The name of the record (e.g., "www.example.com.").

    record_type: The type of the record (e.g., "A", "CNAME").

    record_value: The value(s) for the record.
    """
    client = connect("route53")
    TTL = 300

    recordType = record_type.upper()
    values = record_value if isinstance(record_value, list) else [record_value]

    if recordType == "CNAME" and len(values) != 1:
        print("CNAME must have exactly one value.")
        return

    actions = {
        "create": "CREATE",
        "update": "UPSERT",
        "delete": "DELETE"
    }

    act = actions.get(action.lower())
    if not act:
        print(f"Unsupported action: {action}")
        return

    resource_record_set = {
        "Name": record_name,
        "Type": recordType,
        "TTL": TTL,
        "ResourceRecords": [{"Value": str(v)} for v in values]
    }

    changes = [{
        "Action": act,
        "ResourceRecordSet": resource_record_set
    }]

    try:
        response = client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={"Changes": changes, "Comment": "CLI change"}
        )
        print(f"OK: {act} {recordType} {record_name} -> Change ID: {response['ChangeInfo']['Id']}")
    except ClientError as e:
        print(f"Failed to {action} record: {e}")

@route53.command("list")
def list_route53():
    """
    List all Route53 hosted zones.
    """
    try:
        client = connect("route53")
        response = client.list_hosted_zones()['HostedZones']

        zones = []
        for zone in response:
            zone_id = zone['Id'].split('/')[-1]
            zone_name = zone['Name']
            try:
                tags_res = client.list_tags_for_resource(ResourceType="hostedzone", ResourceId=zone_id)
                tags = {t["Key"]:t["Value"] for t in tags_res["ResourceTagSet"]["Tags"]}

                if tags.get('CreatedBy') == OWNER.lower():
                    zones.append([
                        zone_name,
                        zone_id,
                        OWNER])
            except ClientError:
                continue

        if not zones:
            print(f"No Route53 zones created by {OWNER}")
        else:
            print(f"Route53 zones created by {OWNER}:")
            print(tabulate(zones, headers=["Zone Name", "Zone ID", "OWNER"], tablefmt="grid"))

    except ClientError as e:
        print(f"Error listing zones: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    cli()