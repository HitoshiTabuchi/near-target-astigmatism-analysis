FROM python:3.11-slim
WORKDIR /analysis
COPY . /analysis
RUN pip install --no-cache-dir -e .[test]
ENTRYPOINT ["near-target-pipeline"]
