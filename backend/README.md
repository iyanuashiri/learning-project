# classmatebot-backend

## Setup

virtual environment 
1. Clone the repository `git clone https://github.com/iyanuashiri/classmatebot-project.git`
2. Create a virtual environment `python -m venv venv`
3. Activate the virtual environment `venv\Scripts\activate` on windows or `source venv/bin/activate` on linux
4. Install the requirements `pip install -r requirements.txt`
5. Run the migrations `python manage.py migrate`
6. Run the server `python manage.py runserver`

uv
1. Clone the repository `git clone https://github.com/iyanuashiri/classmatebot-project.git`
2. uv sync
3. uv run python manage.py migrate
4. uv run python manage.py runserver

docker
1. Clone the repository `git clone https://github.com/iyanuashiri/classmatebot-project.git`
2. docker build -t classmatebot-backend .
3. docker run -p 8000:8000 classmatebot-backend



## Cloud services 

1. Twilio
2. SendGrid
3. Render
4. NeonDB
5. Redis.io

## Environment variables

1. SECRET_KEY
2. DATABASE_URL
3. DEBUG
4. TWILIO_ACCOUNT_SID
5. TWILIO_AUTH_TOKEN
6. TWILIO_SERVICE_SID
7. SENDGRID_API_KEY
8. REDIS_URL
9. 


## How to run ngrok
1. Download ngrok from https://ngrok.com/download
2. Unzip the downloaded file
3. Add the ngrok to your system path
4. Open Power Shell as administrator
5. Run ngrok `ngrok http --url=slightly-crisp-pheasant.ngrok-free.app 8000` or 
6. Forwarding https://slightly-crisp-pheasant.ngrok-free.app -> http://localhost:8000 (make sure the port is consistency. )
6. Copy the https url from ngrok
7. Add the https url to the webhook in twilio

## How to run celery
1. uv run celery -A config.celery worker --loglevel=info --pool=solo