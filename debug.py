import ssl
import uvicorn


if __name__=="__main__":
    import sys
    print(f"Python path: {sys.executable}")
    print(f"SSL cert file: {ssl.get_default_verify_paths()}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)