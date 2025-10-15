uv = $(shell which uv)
uv_run = $(uv) run
su_uv_run = sudo $(uv_run)

cloud:
	@echo "Starting cloud MQTT test..."
	@echo "uv path: $(uv)"
	$(su_uv_run) cloud_mqtt_test.py

analyze:
	@echo "Starting analysis..."
	@echo "uv path: $(uv)"
	$(su_uv_run) analyze.py