# NTUSU ITC Backend

## Overview

This is NTUSU ITC Backend repository created on December 2022. It is built using mainly Django REST Framework and a few other dependencies. The old 5 years old repository [here](https://github.com/michac789/NTUSU-Backend) is about to be deprecated, as there are multiple compatibility issues and we want to shift to Single Page Application format where we separate the backend and frontend.

### Table of Contents

1. Development Environment
2. Production Environment
3. Applications Explanation

## Development Environment

### How To Run Development Server

1. Install Docker Desktop based on your operating system and launch the application

2. Move into the project directory where `docker-compose.yml` file is located

3. Install the server using Docker

    ```powershell
        docker-compose up --build
    ```

    Stop using `Ctrl+C`. Re-run this command when you want to start the server again in your local development environment. Database migration is done automatically through docker-compose before the server is started.

    Your server should be up at `localhost:8888`.

### Executing Utility Commands

In order for you to execute other `manage.py` utility commands through Docker container, just add `docker exec -ti SUITC_Backend` or `sudo docker exec -ti SUITC_Backend` (if you're using MAC) in front of your command.

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

Sample data are created using Django Fixtures.

TODO - create fixtures and update

### API Documentation

TODO

## Production Environment

TODO

## Applications Explanation

TODO
