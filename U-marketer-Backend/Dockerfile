FROM python:3.9

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Create .env file for environment variables to be picked up
# (Hugging Face allows injecting secrets as env vars)
# We also copy the source code into /app/app to match python imports (from app.api import ...)
COPY --chown=user ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
