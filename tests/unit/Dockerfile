FROM python:3.12
COPY tests/unit/requirements.txt /
WORKDIR /
RUN pip3 install -r requirements.txt
COPY . /
ENV PATH=/root/.local/bin:$PATH
ENV AI_API_TOKEN="test"
ENV AI_PULL_SECRET="test"
CMD ["python", "-m", "unittest", "discover", "tests/unit/"]