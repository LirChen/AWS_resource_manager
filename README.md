# AWS Platform CLI

A self-service command-line tool for developers to provision and manage AWS resources (EC2, S3, Route53) within safe, pre-defined standards.

## Features

- **EC2 Management**: Create, start, stop, terminate, and list EC2 instances
- **S3 Management**: Create, delete, upload files, and list S3 buckets
- **Route53 Management**: Create, delete, manage DNS records, and list hosted zones
- **Resource Tagging**: Consistent tagging for all resources created by the CLI
- **Safety Constraints**: Built-in limits and confirmations for secure operations

## Prerequisites

- Python 3.7+
- AWS Account with appropriate permissions
- AWS credentials configured

### Required AWS Permissions

Your AWS user/role needs the following permissions:
- `ec2:*` (EC2 management)
- `s3:*` (S3 bucket management)
- `route53:*` (DNS management)

## Installation

### Local Development

1. **Install Git and Python (if not already installed):**
   
   **Windows:**
   - Git: Download from [git-scm.com](https://git-scm.com/download/win) or `winget install Git.Git`
   - Python: Download from [python.org](https://www.python.org/downloads/) or `winget install Python.Python.3`
   
   **macOS:**
   ```bash
   # Using Homebrew:
   brew install git python
   
   # Or download from official sites
   ```
   
   **Linux:**
   ```bash
   # Ubuntu/Debian:
   sudo apt install git python3 python3-pip
   
   # CentOS/RHEL/Fedora:
   sudo yum install git python3 python3-pip
   # or
   sudo dnf install git python3 python3-pip
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/LirChen/AWS_resource_manager.git
   cd AWS_resource_manager
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # On Linux/macOS you might need:
   pip3 install -r requirements.txt
   ```

4. **Configure AWS credentials:** (see AWS Environment Variables Setup below)

### AWS EC2 Instance Setup

#### Amazon Linux

1. **Update system and install prerequisites:**
   ```bash
   sudo yum update -y
   sudo yum install git python3-pip -y
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/LirChen/AWS_resource_manager.git
   cd AWS_resource_manager
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   # If permission issues:
   sudo pip3 install -r requirements.txt
   ```

4. **Configure AWS credentials:**
   ```bash
   export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
   export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

5. **Test the installation:**
   ```bash
   python3 Manager.py --help
   ```

#### Ubuntu

1. **Update system and install prerequisites:**
   ```bash
   sudo apt update
   sudo apt install git python3-pip -y
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/LirChen/AWS_resource_manager.git
   cd AWS_resource_manager
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   # If permission issues:
   sudo pip3 install -r requirements.txt
   ```

4. **Configure AWS credentials:**
   ```bash
   export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
   export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

5. **Test the installation:**
   ```bash
   python3 Manager.py --help
   ```

## AWS Environment Variables Setup

To run this Python integration, you need to configure your AWS credentials as environment variables. This avoids hardcoding secrets inside your code.

### Linux / macOS

Open your shell configuration file (e.g., ~/.bashrc or ~/.zshrc).

Add the following lines at the bottom of the file:
```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-1"
```

Save the file and reload it:
```bash
source ~/.bashrc
```
**or**
```bash
source ~/.zshrc
```

### Windows PowerShell

Run the following commands (they will persist across sessions):
```powershell
setx AWS_ACCESS_KEY_ID "YOUR_ACCESS_KEY"
setx AWS_SECRET_ACCESS_KEY "YOUR_SECRET_KEY"
setx AWS_DEFAULT_REGION "us-east-1"
```

### Command Prompt (temporary, current session only)
```cmd
set AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
set AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
set AWS_DEFAULT_REGION=us-east-1
```

### If you are in PowerShell terminal (inside PyCharm or standalone):
```powershell
$env:AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

Check that they are set:
```powershell
echo $env:AWS_ACCESS_KEY_ID
**Important Notes for EC2:**
- Use `python3` and `pip3` instead of `python` and `pip`
- Default users: `ec2-user` for Amazon Linux, `ubuntu` for Ubuntu
- If you get permission errors with pip, use `sudo`

### Verification

You can verify that the variables are set correctly by running:

**Linux/macOS:**
```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_DEFAULT_REGION
```

**Windows PowerShell:**
```powershell
echo $env:AWS_ACCESS_KEY_ID
echo $env:AWS_SECRET_ACCESS_KEY
echo $env:AWS_DEFAULT_REGION
```

## Usage Examples

### EC2 Instances

#### Create Instance
```bash
python Manager.py ec2 create ubuntu t3.micro
python Manager.py ec2 create amazon-linux t2.small
```

#### Manage Instance
```bash
python Manager.py ec2 manage start i-1234567890abcdef0
python Manager.py ec2 manage stop i-1234567890abcdef0
python Manager.py ec2 manage terminate i-1234567890abcdef0
```

#### List Instances
```bash
python Manager.py ec2 list
```

### S3 Buckets

#### Create Bucket
```bash
python Manager.py s3 create private
python Manager.py s3 create public  # Requires confirmation
```

#### Upload File
```bash
python Manager.py s3 upload /path/to/file.txt bucket-name file.txt
```

#### Delete Bucket
```bash
python Manager.py s3 delete s3-bucket-lirchen-abc123
```

#### List Buckets
```bash
python Manager.py s3 list
```

### Route53 DNS

#### Create Hosted Zone
```bash
python Manager.py route53 create example.com
```

#### Manage DNS Records
```bash
# Create A record
python Manager.py route53 manage create Z1D633PJN98FT9 www.example.com A 192.168.1.1

# Update CNAME record
python Manager.py route53 manage update Z1D633PJN98FT9 api.example.com CNAME api.provider.com

# Delete record
python Manager.py route53 manage delete Z1D633PJN98FT9 old.example.com A 192.168.1.100
```

#### Delete Hosted Zone
```bash
python Manager.py route53 delete Z1D633PJN98FT9
```

#### List Hosted Zones
```bash
python Manager.py route53 list
```

## Safety Constraints

### EC2 Constraints
- **Instance Types**: Only `t3.micro` and `t2.small` allowed
- **Hard Limit**: Maximum 2 running instances at any time
- **AMI Options**: Latest Ubuntu or Amazon Linux only

### S3 Constraints
- **Public Buckets**: Requires explicit confirmation
- **Bucket Naming**: Automatic unique naming with random suffix
- **Access Control**: Public buckets use bucket policies (not ACLs)

### Route53 Constraints
- **Zone Management**: Only CLI-created zones can be modified
- **Record Management**: Only records in CLI-created zones can be managed

## Tagging Convention

All resources created by this CLI are tagged with:
- `CreatedBy`: Owner identifier (configurable in code)
- `Visibility`: For S3 buckets (public/private)

**Example Tags:**
```json
{
  "CreatedBy": "lirchen",
  "Visibility": "private"
}
```

## Configuration

Edit the `OWNER` variable in `Manager.py` to set your identifier:
```python
OWNER = "your-username"
```

## Error Handling

The CLI provides clear error messages for common scenarios:
- Resource not found
- Permission denied
- Invalid resource states
- AWS service limits exceeded

## Cleanup Instructions

### Clean Up All Resources

**EC2 Instances:**
```bash
python Manager.py ec2 list
# Terminate each instance manually:
python Manager.py ec2 manage terminate i-xxxxxxxxx
```

**S3 Buckets:**
```bash
python Manager.py s3 list
# Delete each bucket:
python Manager.py s3 delete bucket-name
```

**Route53 Zones:**
```bash
python Manager.py route53 list
# Delete each zone:
python Manager.py route53 delete zone-id
```

## Troubleshooting

### Common Issues

**"Unable to locate credentials"**
- Check that AWS environment variables are set correctly
- Verify AWS credentials are valid

**"Access Denied"**
- Ensure your AWS user has the required permissions
- Check if MFA is required for your account

**"Cannot create public bucket"**
- AWS security settings may block public access
- Bucket will be created as private for security

**"Bucket name already exists"**
- S3 bucket names must be globally unique
- The CLI uses random suffixes to avoid conflicts

### Getting Help

Use `--help` with any command:
```bash
python Manager.py --help
python Manager.py ec2 --help
python Manager.py s3 create --help
```

## Security Best Practices

- ✅ No secrets stored in repository
- ✅ Uses AWS roles/profiles for authentication
- ✅ Consistent resource tagging
- ✅ Built-in safety constraints
- ✅ Confirmation prompts for destructive actions
- ✅ Private-by-default for S3 buckets

## Dependencies

```txt
boto3>=1.26.0
botocore>=1.29.0
click>=8.0.0
tabulate>=0.9.0
```

---

**Note**: This tool is designed for development environments. Always review and test in non-production environments first.
