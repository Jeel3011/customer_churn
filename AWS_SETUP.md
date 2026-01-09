# AWS S3 & GitHub CI/CD Setup Guide

## ✅ Current Status
- Application is **LIVE** at: `http://13.51.45.223:8000` and `http://13.51.45.223:8501`
- Publicly accessible on internet ✓

## Step 1: Create S3 Bucket

```bash
# Create S3 bucket for predictions
aws s3 mb s3://customer-churn-predictions-$(date +%s) --region us-east-1
```

Note the bucket name for later.

## Step 2: Create IAM Role for EC2

1. Go to **AWS Console → IAM → Roles**
2. Click "Create Role"
3. Select "EC2" as trusted entity
4. Add policy: `AmazonS3FullAccess` (or create custom policy with specific bucket)
5. Name it: `ChurnEC2Role`

Then attach to EC2 instance:
```bash
# Attach role to EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id <your-instance-id> \
  --iam-instance-profile Name=ChurnEC2Role
```

## Step 3: Set GitHub Secrets

Go to **GitHub Repository → Settings → Secrets and Variables → Actions**

Add these secrets:
```
EC2_HOST            = 13.51.45.223
EC2_USER            = ec2-user
EC2_SSH_KEY         = [paste content of ~/Desktop/churn_key.pem]
S3_BUCKET           = [your-bucket-name]
AWS_REGION          = us-east-1
AWS_ACCESS_KEY_ID   = [from IAM user]
AWS_SECRET_ACCESS_KEY = [from IAM user]
```

## Step 4: Deploy Latest Code

1. Commit changes:
```bash
git add .
git commit -m "feat: Add S3 and CI/CD integration"
git push origin main
```

2. GitHub Actions will automatically trigger deployment
3. Check **Actions** tab in GitHub for deployment status

## Step 5: Test S3 Integration

Upload a CSV file through the UI. Predictions should be saved to S3:
- S3 location: `s3://[bucket-name]/predictions/`
- Response will include `s3_file` key with file path

## Environment Variables

For manual deployment:
```bash
export S3_BUCKET="customer-churn-predictions"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

docker-compose up -d
```

## Troubleshooting

### S3 uploads failing:
- Check IAM permissions on EC2 role
- Verify S3 bucket exists and is accessible
- Check CloudWatch logs for detailed errors

### CI/CD not triggering:
- Verify GitHub secrets are set correctly
- Check SSH key has proper permissions (600)
- Review GitHub Actions logs for errors

### API can't connect to S3:
- Ensure EC2 instance has IAM role with S3 permissions
- If using AWS credentials, verify they have S3 access
- Check security groups allow EC2 outbound traffic
