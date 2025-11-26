.PHONY: help signup login logout profile profile-update change-password groups groups-create groups-detail groups-list groups-members

API_URL = http://localhost:8000/api/auth
GROUPS_URL = http://localhost:8000/api/groups
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
	@echo "  make groups          - List user's groups"
	@echo "  make groups-create   - Create a new group"
	@echo "  make groups-detail   - Get group details"
	@echo "  make groups-list     - List group members"
	@echo "  make groups-members  - Add member to group"

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

groups:
	@LOGIN_RESPONSE=$$(curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}'); \
	ACCESS=$$(echo $$LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))"); \
	curl -X GET $(GROUPS_URL)/ \
		-H "Authorization: Bearer $$ACCESS" \
		-H "Content-Type: application/json" \
		-s | python3 -m json.tool

groups-create:
	@LOGIN_RESPONSE=$$(curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}'); \
	ACCESS=$$(echo $$LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))"); \
	curl -X POST $(GROUPS_URL)/ \
		-H "Authorization: Bearer $$ACCESS" \
		-H "Content-Type: application/json" \
		-d '{"name":"Test Group","description":"A test group"}' \
		-s | python3 -m json.tool

groups-detail:
	@LOGIN_RESPONSE=$$(curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}'); \
	ACCESS=$$(echo $$LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))"); \
	GROUP_RESPONSE=$$(curl -s -X POST $(GROUPS_URL)/ -H "Authorization: Bearer $$ACCESS" -H "Content-Type: application/json" -d '{"name":"Detail Group"}'); \
	GROUP_ID=$$(echo $$GROUP_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))"); \
	curl -X GET $(GROUPS_URL)/$$GROUP_ID/ \
		-H "Authorization: Bearer $$ACCESS" \
		-H "Content-Type: application/json" \
		-s | python3 -m json.tool

group-members-list:
	@LOGIN_RESPONSE=$$(curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}'); \
	ACCESS=$$(echo $$LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))"); \
	GROUP_RESPONSE=$$(curl -s -X POST $(GROUPS_URL)/ -H "Authorization: Bearer $$ACCESS" -H "Content-Type: application/json" -d '{"name":"Members Group"}'); \
	GROUP_ID=$$(echo $$GROUP_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))"); \
	curl -X GET $(GROUPS_URL)/$$GROUP_ID/members/ \
		-H "Authorization: Bearer $$ACCESS" \
		-H "Content-Type: application/json" \
		-s | python3 -m json.tool

add-group-member:
	@LOGIN_RESPONSE=$$(curl -s -X POST $(API_URL)/login/ -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"securepassword123"}'); \
	ACCESS=$$(echo $$LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))"); \
	GROUP_RESPONSE=$$(curl -s -X POST $(GROUPS_URL)/ -H "Authorization: Bearer $$ACCESS" -H "Content-Type: application/json" -d '{"name":"Add Member Group"}'); \
	GROUP_ID=$$(echo $$GROUP_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))"); \
	MEMBER_RESPONSE=$$(curl -s -X POST $(API_URL)/signup/ -H "Content-Type: application/json" -d '{"email":"member@example.com","password":"securepassword123"}'); \
	USER_ID=$$(echo $$MEMBER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))"); \
	curl -X POST $(GROUPS_URL)/$$GROUP_ID/members/ \
		-H "Authorization: Bearer $$ACCESS" \
		-H "Content-Type: application/json" \
		-d "{\"user_id\":\"$$USER_ID\"}" \
		-s | python3 -m json.tool
