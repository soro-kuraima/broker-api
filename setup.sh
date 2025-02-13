# setup.sh
#!/bin/bash

# Create main app directory
mkdir -p app/{models,schemas,controllers,services,core,utils}

# Create __init__.py files
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/controllers/__init__.py
touch app/services/__init__.py
touch app/core/__init__.py
touch app/utils/__init__.py

# Create main application files
touch app/main.py
touch app/config.py
touch app/dependencies.py
touch app/database.py

# Create model files
touch app/models/user.py
touch app/models/number.py

# Create schema files
touch app/schemas/user.py
touch app/schemas/number.py

# Create controller files
touch app/controllers/auth.py
touch app/controllers/csv_operations.py
touch app/controllers/websocket.py

# Create service files
touch app/services/auth.py
touch app/services/csv_manager.py
touch app/services/number_generator.py

# Create core files
touch app/core/security.py
touch app/core/exceptions.py

# Create utils files
touch app/utils/helpers.py

# Make the script executable
chmod +x setup.sh

echo "Project structure created successfully!"

