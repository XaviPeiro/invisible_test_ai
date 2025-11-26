.PHONY: help signup login

API_URL = http://localhost:8000/api/auth

help:
	@echo "Available commands:"
	@echo "  make signup  - Sign up a new user"
	@echo "  make login   - Login and get JWT tokens"

signup:
	@curl -X POST $(API_URL)/signup/ \
		-H "Content-Type: application/json" \
		-d '{"email":"user@example.com","password":"securepassword123","username":"testuser"}' \
		-s | python3 -m json.tool

login:
	@curl -X POST $(API_URL)/login/ \
		-H "Content-Type: application/json" \
		-d '{"email":"user@example.com","password":"securepassword123"}' \
		-s | python3 -m json.tool
