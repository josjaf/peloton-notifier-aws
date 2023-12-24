docker build -t peloton-notifier-test .
docker run -v ~/.aws:/root/.aws -e PELOTON_CREDENTIALS_PARAM="/peloton/json" -it peloton-notifier-test sh
