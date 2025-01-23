FROM python:3.9

# Définition des arguments pour le proxy (passés par GitLab CI/CD)
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# Définition des variables d'environnement dans le conteneur
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY
ENV no_proxy=$NO_PROXY

# Éviter les prompts interactifs de apt-get
ENV DEBIAN_FRONTEND=noninteractive


# Set working directory
WORKDIR /code

# Copy application files
COPY . /code


RUN apt-get update && apt-get install -y curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /root/.bashrc && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /etc/environment

# Ensure Rust and Cargo are installed
RUN /root/.cargo/bin/cargo --version

# Set Cargo path explicitly before installing Python dependencies
ENV PATH="/root/.cargo/bin:$PATH"

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Set environment variables for service dependencies
ENV MONGO_HOST=mongo-service
ENV PHOTOGRAPHER_HOST=photographer-service
ENV PHOTO_HOST=photo-service


# Run the application with auto-reload
CMD ["uvicorn", "albums_service:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]

