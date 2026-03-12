FROM python:3.12-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin && \
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
WORKDIR /app
RUN pip install .
COPY docscansec/ ./docscansec/
ENTRYPOINT ["python", "-m", "docscansec.main"]
CMD ["--help"]