# Record the resolved image digest in each run; author OS/Python were not pinned.
ARG BASE_IMAGE=python@sha256:8fb099199b9f2d70342674bd9dbccd3ed03a258f26bbd1d556822c6dfc60c317
FROM ${BASE_IMAGE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN openssl version && dpkg-query -W > /tmp/os-packages.txt
COPY requirements.txt /harness/requirements.txt
RUN python -m pip install --no-cache-dir -r /harness/requirements.txt \
    && python -m pip freeze --all > /harness/installed-packages.txt \
    && mv /tmp/os-packages.txt /harness/os-packages.txt
COPY baseline /baseline
COPY mp-spdz /mp-spdz
COPY replay_original.py identity.json source_manifest.json /harness/
RUN mkdir -p /baseline/evaluation/evaluation_storage /results /run \
    && chmod -R a-w /baseline /mp-spdz /harness
USER 1000:1000
WORKDIR /run
ENTRYPOINT ["python", "/harness/replay_original.py"]
