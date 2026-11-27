from __future__ import annotations


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
