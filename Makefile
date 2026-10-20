PYTHON ?= python
RAW_CONFIG ?= config/raw_files.yml

.PHONY: install test test-public test-private frozen raw clean
install:
	$(PYTHON) -m pip install -e .[test]

test: test-public

test-public:
	$(PYTHON) -m pytest -q -m "not private_data"

test-private:
	NEAR_TARGET_RAW_CONFIG=$(RAW_CONFIG) $(PYTHON) -m pytest -q -m private_data

frozen:
	near-target-pipeline frozen --output outputs/frozen_release

raw:
	near-target-pipeline raw --raw-config $(RAW_CONFIG) --output outputs/raw_verification

clean:
	rm -rf outputs/frozen_release outputs/raw_verification .pytest_cache
