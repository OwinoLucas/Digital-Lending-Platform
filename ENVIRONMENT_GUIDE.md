# Development vs Production Mode Guide

## Modes of Operation

The LMS application can run in two modes:

1. **Development Mode**: Uses mock services locally, simulates API calls, and doesn't require network connectivity to external services. Ideal for local development and testing.

2. **Production Mode**: Connects to actual external APIs, requires network connectivity to those services. Used for staging and production environments.

## Setting Up Your Environment

### Environment Variables File (.env)

The application uses a `.env` file to manage configuration. To set up your environment:

1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file and update the values according to your environment.

### Switching Between Modes

You can set the mode using the `DJANGO_ENV` environment variable:

#### For Linux/Mac:

```bash
# Development Mode
export DJANGO_ENV=development
python manage.py runserver

# Production Mode
export DJANGO_ENV=production  # or don't set it (defaults to production)
python manage.py runserver
```

#### For Windows:

```powershell
# Development Mode
set DJANGO_ENV=development
python manage.py runserver

# Production Mode
set DJANGO_ENV=production  # or don't set it (defaults to production)
python manage.py runserver
```

### Checking Current Mode

You can check which mode you're currently running in by opening the Django shell:

```bash
python manage.py shell
```

Then run:

```python
import os
print(os.environ.get('DJANGO_ENV', 'production'))
```

## Automatic Fallback to Development Mode

The application has built-in fallback capabilities for network connectivity issues:

1. If you set `DJANGO_ENV=production` but the external services are unreachable:
   - The system will automatically fall back to using mock services
   - Error logs will be generated showing the connectivity issue
   - Warning logs will indicate the fallback to development mode

2. Network errors that trigger automatic fallback include:
   - Connection errors (service unavailable, network unreachable)
   - Timeouts (service taking too long to respond)
   - DNS resolution failures

3. This fallback mechanism ensures:
   - The application continues to function even without internet access
   - Development can proceed without waiting for external service availability
   - Testing can be performed in offline environments

## Configuration Settings

The application uses the following environment variables:

1. **Environment Settings**:
   - `DJANGO_ENV`: Set to 'development' or 'production'

2. **Django Settings**:
   - `SECRET_KEY`: Django's secret key
   - `DEBUG`: Set to 'True' or 'False'

3. **Database Settings**:
   - `DB_ENGINE`: Database engine (e.g., django.db.backends.mysql)
   - `DB_NAME`: Database name
   - `DB_USER`: Database username
   - `DB_PASSWORD`: Database password
   - `DB_HOST`: Database host
   - `DB_PORT`: Database port

4. **Scoring Engine Settings**:
   - `SCORING_ENGINE_BASE_URL`: Base URL for the scoring engine API
   - `MAX_SCORING_RETRIES`: Maximum number of retries for scoring API calls
   - `SCORING_RETRY_DELAY`: Delay between retry attempts

5. **CBS Settings**:
   - `CBS_KYC_WSDL_URL`: WSDL URL for KYC service
   - `CBS_TRANSACTION_WSDL_URL`: WSDL URL for transaction service
   - `CBS_USERNAME`: Username for CBS authentication
   - `CBS_PASSWORD`: Password for CBS authentication

## How it Works

The configuration in `settings.py` includes logic to detect the environment and configure the application accordingly:

```python
# In settings.py
from dotenv import load_dotenv
load_dotenv()

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'production')
USE_LOCAL_SCORING = DJANGO_ENV == 'development'
USE_LOCAL_CBS = DJANGO_ENV == 'development'
```

This setup allows you to switch between environments without changing any code. When in development mode, the application will use mock services; in production mode, it will connect to real external services. 