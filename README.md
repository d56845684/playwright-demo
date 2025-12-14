# playwright-demo

A simple Flask demo app that lists campsite availability and allows CSV downloads. Default credentials: `demo` / `demo123`.

## Local development
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   flask --app app run --host 0.0.0.0 --port 5000
   ```

## Docker deployment
1. Build the image:
   ```bash
   docker build -t playwright-demo .
   ```
2. Run the container:
   ```bash
   docker run -d \
     -p 5000:5000 \
     --name playwright-demo \
     playwright-demo
   ```
3. Visit [http://localhost:5000](http://localhost:5000) and sign in with the demo credentials.

### Notes
- The container listens on port `5000` by default; adjust the published port as needed.
- Update `app.secret_key` in `app.py` to a secure value before deploying to production.
