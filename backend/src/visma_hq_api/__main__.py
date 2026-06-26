"""Run the API: `python -m visma_hq_api` or `visma-hq-api`."""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run("visma_hq_api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
