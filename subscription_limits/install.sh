#!/bin/bash

# Subscription Limits Manager Installation Script
# For Odoo 17.0+

echo "🚀 Installing Subscription Limits Manager for Odoo 17..."

# Check if we're in the right directory
if [ ! -f "__manifest__.py" ]; then
    echo "❌ Error: Please run this script from the subscription_limits module directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [ "$(echo "$python_version >= 3.8" | bc -l)" -eq 0 ]; then
    echo "❌ Error: Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if Odoo is installed
if ! command -v odoo &> /dev/null; then
    echo "⚠️  Warning: Odoo command not found in PATH"
    echo "   Make sure Odoo is installed and in your PATH"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p static/src/sounds
mkdir -p static/description

# Set permissions
echo "🔐 Setting proper permissions..."
chmod -R 755 .
chmod +x install.sh

# Check for required dependencies
echo "📦 Checking dependencies..."
python3 -c "
import sys
required_modules = ['odoo']
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f'❌ Missing required modules: {missing_modules}')
    sys.exit(1)
else:
    print('✅ All required modules are available')
"

if [ $? -ne 0 ]; then
    echo "❌ Error: Missing required dependencies"
    exit 1
fi

# Create a simple test to verify the module structure
echo "🧪 Testing module structure..."
python3 -c "
import os
import sys

required_files = [
    '__manifest__.py',
    '__init__.py',
    'models/__init__.py',
    'models/subscription_plan.py',
    'models/subscription_user.py',
    'views/subscription_plan_views.xml',
    'views/subscription_user_views.xml',
    'security/ir.model.access.csv'
]

missing_files = []
for file in required_files:
    if not os.path.exists(file):
        missing_files.append(file)

if missing_files:
    print(f'❌ Missing required files: {missing_files}')
    sys.exit(1)
else:
    print('✅ All required files are present')
"

if [ $? -ne 0 ]; then
    echo "❌ Error: Module structure is incomplete"
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Restart your Odoo server"
echo "2. Go to Apps menu in Odoo"
echo "3. Search for 'Subscription Limits Manager'"
echo "4. Click Install"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "🆘 Need help? Check the documentation or contact support"
echo "" 