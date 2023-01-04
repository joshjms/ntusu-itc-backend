# SSO

## JWT Authentication

    a
    bfd

### Explanation

Simple flow on how JWT works (after user registration):

- Get `test`

### `[POST] /sso/token/`

Takes the username and password of the user. If the the credentials are valid, return access and refresh token to prove the authentication of those credentials. Return 401 error instead if the credentials are invalid (user not found, or wrong password given).

Sample Code:

    fetch('http://localhost:8888/sso/token/',
    {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(
            {
                'username': 'Sample User 1',
                'password': '1048576#',
            }
        ),
    })

### `[POST] /sso/token/refresh/`

Takes a refresh token and returns an access token if the refresh token is valid. Returns 401 if token is invalid or has expired.

### `[POST] /sso/token/verify/`

Takes a token (any token, can be acccess or refresh token), verify whether the token is still valid or not. If the token is still valid, returns 200, otherwise 401.

## User Creation

## Other Password Related Routes

###
> method
> sdfs
> dfsdf

```
dsfsdf
```