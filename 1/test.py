from requests import get
print(get('http://127.0.0.1:8080/api/users').json())
print(get('http://127.0.0.1:8080/api/users/2').json())
print(get('http://127.0.0.1:8080/api/companies').json())
print(get('http://127.0.0.1:8080/api/companies/3').json())
