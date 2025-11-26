.PHONY: help signup login logout profile profile-update change-password

API_URL = http://localhost:8000/api/auth
TOKEN = $(shell curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")
REFRESH_TOKEN = $(shell curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('refresh', ''))")

help:
	@echo "Available commands:"
	@echo "  make signup          - Sign up a new user"
	@echo "  make login           - Login and get JWT tokens"
	@echo "  make logout          - Logout and blacklist refresh token"
	@echo "  make profile         - Get current user profile"
	@echo "  make profile-update  - Update user profile"
	@echo "  make change-password - Change user password"

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

logout:
	@LOGIN_RESPONSE=$$(curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}'); \
	ACCESS=$$(echo $$LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))"); \
	REFRESH=$$(echo $$LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('refresh', ''))"); \
	curl -X POST $(API_URL)/logout/ \
		-H "Authorization: Bearer $$ACCESS" \
		-H "Content-Type: application/json" \
		-d "{\"refresh\":\"$$REFRESH\"}" \
		-s | python3 -m json.tool

profile:
	@curl -X GET $(API_URL)/profile/ \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-s | python3 -m json.tool

profile-update:
	@curl -X PUT $(API_URL)/profile/ \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"username":"updateduser"}' \
		-s | python3 -m json.tool

change-password:
	@curl -X POST $(API_URL)/profile/change-password/ \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"old_password":"securepassword123","new_password":"newpassword123"}' \
		-s | python3 -m json.tool
