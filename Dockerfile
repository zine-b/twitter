FROM python:3.7

WORKDIR /twitter

COPY . /twitter

# Install OpenJDK 11 from AdoptOpenJDK
RUN apt-get update && apt-get install -y gnupg
RUN echo "deb http://adoptopenjdk.jfrog.io/adoptopenjdk/deb buster main" > /etc/apt/sources.list.d/adoptopenjdk.list

# Download the AdoptOpenJDK GPG key manually and add it to the keyring
RUN curl -fsSL https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | gpg --dearmor -o /usr/share/keyrings/adoptopenjdk-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/adoptopenjdk-archive-keyring.gpg] http://adoptopenjdk.jfrog.io/adoptopenjdk/deb buster main" > /etc/apt/sources.list.d/adoptopenjdk.list

# Install OpenJDK 11
RUN apt-get update && apt-get install -y adoptopenjdk-11-hotspot

# Install any dependencies
RUN pip install -r ./requirements.txt
RUN pip install pyyaml

CMD ["python", "run.py"]
