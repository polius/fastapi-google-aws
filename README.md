<div align="center">
<h1 align="center">FastAPI Google OAuth2 AWS</h1>
<img src="/assets/screenshot.png" alt="Screenshot" width="500" />
</div>

<br>

A FastAPI web application featuring secure Google OAuth2 authentication for user login and seamless AWS access via OAuth2. Designed for easy deployment with Docker.

## Features

- Secure login with Google accounts (OAuth2)
- Seamless AWS access via AssumeRoleWithWebIdentity
- Simple and modular FastAPI project structure
- Ready-to-use Docker container

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- A Gmail account

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/polius/fastapi-google-aws.git
cd fastapi-google-aws
```

### 2. Configure Google Cloud OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Navigate to **APIs & Services → Credentials**.
4. Create an **OAuth 2.0 Client ID** and set:
- **Authorized JavaScript origins**: http://localhost
- **Authorized redirect URIs**: http://localhost/api/callback
5. Download the generated JSON credentials file.

### 2. Create an AWS Identity Provider

1. Go to IAM → Identity providers → Add provider.
2. Configure the provider:
- Provider type: OpenID Connect
- Provider URL: https://accounts.google.com
- Audience: <Google OAuth2 Client ID>

### 3. Create an AWS Role with the Trust Relationship

1. Go to IAM → Roles → Create role.
2. Choose "Custom trust policy".
3. Use the following Trust Relationship JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/accounts.google.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "accounts.google.com:aud": "<GOOGLE_OAUTH2_CLIENT_ID>",
          "accounts.google.com:email": "<your@email.com>"
        },
      }
    }
  ]
}
```

- Replace `<AWS_ACCOUNT_ID>` with the AWS account where the Role will be created.
- Replace `<GOOGLE_OAUTH2_CLIENT_ID>` with your Google OAuth2 Client ID.
- Replace `<your@email.com>` with the specific user email(s) allowed to assume this role.

### 4. Configure environment variables

1. Edit the `api/.env` file.
2. Add the Google credentials from the downloaded JSON file.
3. Add the AWS Role ARN for the role you just created.

### 5. Build the Docker image

```bash
docker buildx build -t fastapi-google-aws --compress --load .
```

### 6. Run the container

```bash
docker run --rm -p 80:80 fastapi-google-aws
```

### 7. Access the application

Open http://localhost in your browser.

### 8. Clean up (optional)

```bash
docker rmi fastapi-google-aws
```

## License

This project is licensed under the [MIT License](LICENSE).