uv = $(shell which uv)
uv_run = $(uv) run
su_uv_run = sudo $(uv_run)

nat_example:
	@echo "Starting Mininet NAT example..."
	@echo "uv path: $(uv)"
	$(su_uv_run) mininet_nat_example.py

analyze:
	@echo "Starting analysis..."
	@echo "uv path: $(uv)"
	$(su_uv_run) analyze.py

cloud/simulation:
	@echo "Starting cloud MQTT test..."
	@echo "uv path: $(uv)"
	$(su_uv_run) cloud_mqtt_test.py

cloud/all:
	@echo "Starting full cloud test (simulation + analysis)..."
	@echo "uv path: $(uv)"
	$(su_uv_run) cloud_mqtt_test.py
	$(su_uv_run) analyze.py