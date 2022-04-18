# Base image from ubuntu
FROM python:3.8.10

# Create working directory for the container
WORKDIR /pipeline-api

# Port which will run the API
ARG PORT=5020
ENV API_PORT=$PORT
EXPOSE $PORT

# Adding root directory as python path
ENV PYTHONPATH "${PYTHONPATH}:/pipeline-api"

# Copy project content into the working directory
COPY . ./api

# Install dependencies
RUN pip3 install -r ./api/requirements.txt

# Execute API server
CMD ["python3", "./api/main.py"]
