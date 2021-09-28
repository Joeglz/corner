# credijusto

https://credijusto-jose.herokuapp.com/docs#/

Exposes the current exchange rate of USD to MXN from three different sources in the same endpoint.

### Running 
    Build the image: docker-compose build
    Run the container: docker-compose up -d
### Hostname
  http://localhost:8008

### Create User
    Use the default endpoint /users 
    try it out
    Fill the json
    Execute
    
### Get current exchange rate
    Authorize
    Log in whit the user previusly created
    Use the default endpoint /date 
    Execute
    
### Run test
    pytest app/test.py
