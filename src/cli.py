import os
from src.main import create_app


# Use FLASK_CONFIG from environment or default to 'dev'
config_name = os.environ.get("FLASK_CONFIG", "dev")
app = create_app(config_name)

# Run the application
if __name__ == "__main__":
    # Provides a default entry point for running the application
    port = int(os.environ.get("APP_PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
