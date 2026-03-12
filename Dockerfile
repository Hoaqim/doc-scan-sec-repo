FROM anchore/syft:latest AS syft
FROM anchore/grype:latest AS grype

FROM python:3.12-slim

COPY --from=syft /syft /usr/local/bin/syft
COPY --from=grype /grype /usr/local/bin/grype

WORKDIR /app

COPY pyproject.toml .
COPY docscansec/ ./docscansec/

RUN pip install --no-cache-dir .
ENTRYPOINT ["python", "-m", "docscansec.main"]
CMD ["--help"]