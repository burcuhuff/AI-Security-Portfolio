## Local Environment Setup

To isolate this system's dependencies from the rest of the portfolio, set up a dedicated virtual environment:

```bash
# Navigate to this directory
cd privacy-audit-system

# Create and activate the fresh environment
python3 -m venv venv
source venv/bin/activate

# Install required development dependencies
pip install faker pytest
```

## Key Dependencies

*   **`faker`**: Used to generate synthetic system access events, mock analyst profiles, and simulate adversarial behavior without exposing real system data.
*   **`pytest`**: The core testing framework used to validate that the audit logger correctly intercepts queries, formats JSONL logs, and flags privacy violations.

## Development Phases

1.  **Phase 1: Structural Logging (Current)** — Capturing operational metadata (Timestamps, User IDs, Action types) into structured `.jsonl` files.
2.  **Phase 2: Quasi-Identifier Monitoring** — Inspecting query structures to flag high-risk demographic combinations (`zip_code` + `age` + `gender`).
3.  **Phase 3: Privacy Budget Tracking** — Interfacing with Differential Privacy algorithms to monitor cumulative Epsilon ($\epsilon$) consumption.

## Running Tests

Ensure your virtual environment is active, then run the test suite:

```bash
pytest
```