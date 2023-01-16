# NTUSU ITC Backend

## Overview

This is NTUSU ITC Backend repository created on December 2022. It is built using mainly Django REST Framework and a few other dependencies. The old 5 years old repository [here](https://github.com/michac789/NTUSU-Backend) (private repository, invitation is required to access) is about to be deprecated, as there are multiple compatibility issues and we want to shift to Single Page Application format where we separate the backend and frontend.

### Table of Contents

1. Development Environment
2. Production Environment
3. Applications Explanation

## Development Environment

### How To Run Development Server

1. Install Docker Desktop based on your operating system ([MAC](https://docs.docker.com/desktop/install/mac-install/) / [Windows](https://docs.docker.com/desktop/install/windows-install/) / [Linux](https://docs.docker.com/desktop/install/linux-install/)) and launch the application

2. Clone this repository and move into the project directory where `docker-compose.yml` file is located

3. Install the server using Docker

   ```powershell
       docker-compose up --build
   ```

   Stop using `Ctrl+C`. Re-run this command when you want to start the server again in your local development environment.

   Your server should be up at `localhost:8888`. If this is your first time running the development environment, please do step 4 as shown below. The application will not run properly if you do not perform database migration.

4. Initialize database migration

   Using another terminal, execute the following command:

   ```powershell
       docker exec -ti SUITC_Backend python manage.py migrate
   ```

   Note: you might need to add `sudo` if you're using MAC

   You should do this when it is your first time running the development environment, and anytime there are new database migrations.

### Troubleshoot

This section is to document any problems that might occur when running the development environment along with its solution, as we all are using different devices which might have slightly different behaviour.

- Note: For Macbook M1/M2, you must run this before doing all required steps below:

```powershell
    softwareupdate --install-rosetta
    export DOCKER_DEFAULT_PLATFORM=linux/amd64
```

### Executing Utility Commands

In order for you to execute other `manage.py` utility commands through Docker container, just add `docker exec -ti SUITC_Backend` (add `sudo` if you're using MAC) in front of your command. Please ensure that the server is indeed running, open another terminal if needed.

For example, to create new migrations you can run:

```powershell
    docker exec -ti SUITC_Backend python manage.py makemigrations
```

### Testing

Everytime you add new features, please create the appropriate test cases. You can run this command to run all the test cases:

```powershell
    docker exec -ti SUITC_Backend python manage.py test
```

Automatic CI testing is enforced everytime a pull request or a push is done to the main branch.

### Superuser & Sample Data

Sample data are generated using Django Fixtures. It is used to populate your database (stored in Docker Volumes) with some sample data so that every person do not have to do it on their own manually. You can load the data by opening another terminal and run the command:

```powershell
    docker exec -ti SUITC_Backend python manage.py loaddata sample_user
```

Running this command will give you superuser access with the username `superuser` and password `123`. Other sample data can be seen on the fixtures folder (password for other sample user: 1048576#).

Warning: running the command may overwrite some existing data

### API Documentation

There are 2 types of documentation provided here:

- Automatic Documentation using Swagger UI

- Manual Documentation in the `docs` app by writing markdown files (stored locally in this repository)

## Production Environment

The server is deployed using AWS [here](http://ntusu-itc-backend.ap-southeast-1.elasticbeanstalk.com/) using Python 3.8 running on Linux2 Ver 3.4.3 machine. Current database is using AWS RDS Multi DB Cluster with MySQL engine. Database related configurations are set up through environment variables in the EB environment. Currently, the server has no certificate yet, meaning that we can't use 'https' yet to connect the live server.

## Applications Explanation

### Portal

### SSO

### UFacility

### ~~Inventory~~

### Event

### Docs

### StarsWar

### ~~ULocker~~

### Workshop

### Communication

### Games

### UShop
