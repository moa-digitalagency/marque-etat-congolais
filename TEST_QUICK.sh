#!/bin/bash

# Quick Verification Script for CSS & Assets Fixes
# Run this script to verify all fixes are in place

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           CSS & ASSETS FIX - QUICK VERIFICATION SCRIPT            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

BASE_PATH="/Users/moadigitalagency/marque-etat-congolais"
ERRORS=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "Checking directory structure..."

# Check directories
for dir in "static/css" "static/font" "static/font/cooper-hewitt" "static/js" "static/img"; do
    if [ -d "$BASE_PATH/$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir"
    else
        echo -e "${RED}✗${NC} $dir (NOT FOUND)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "Checking CSS files..."

# Check CSS files
for file in "tokens.css" "components.css" "custom.css"; do
    if [ -f "$BASE_PATH/static/css/$file" ]; then
        size=$(wc -c < "$BASE_PATH/static/css/$file")
        echo -e "${GREEN}✓${NC} static/css/$file ($size bytes)"
    else
        echo -e "${RED}✗${NC} static/css/$file (NOT FOUND)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "Checking font files..."

# Check key font files
for font in "CooperHewitt-Bold.otf" "CooperHewitt-Light.otf" "CooperHewitt-Book.otf"; do
    if [ -f "$BASE_PATH/static/font/cooper-hewitt/$font" ]; then
        size=$(wc -c < "$BASE_PATH/static/font/cooper-hewitt/$font")
        echo -e "${GREEN}✓${NC} static/font/cooper-hewitt/$font"
    else
        echo -e "${RED}✗${NC} static/font/cooper-hewitt/$font (NOT FOUND)"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "Checking configuration..."

# Check constants.py for corrected font path
if grep -q "FONT_FILE = '../font/cooper-hewitt/CooperHewitt-Bold.otf'" "$BASE_PATH/config/constants.py"; then
    echo -e "${GREEN}✓${NC} config/constants.py - FONT_FILE path corrected"
else
    echo -e "${RED}✗${NC} config/constants.py - FONT_FILE path not corrected"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "Checking template updates..."

# Check base.html for CSS links
if grep -q "tokens.css" "$BASE_PATH/templates/base.html"; then
    echo -e "${GREEN}✓${NC} templates/base.html - tokens.css linked"
else
    echo -e "${RED}✗${NC} templates/base.html - tokens.css NOT linked"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "components.css" "$BASE_PATH/templates/base.html"; then
    echo -e "${GREEN}✓${NC} templates/base.html - components.css linked"
else
    echo -e "${RED}✗${NC} templates/base.html - components.css NOT linked"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "custom.css" "$BASE_PATH/templates/base.html"; then
    echo -e "${GREEN}✓${NC} templates/base.html - custom.css linked"
else
    echo -e "${RED}✗${NC} templates/base.html - custom.css NOT linked"
    ERRORS=$((ERRORS + 1))
fi

# Check if Tailwind is still loaded
if grep -q "cdn.tailwindcss.com" "$BASE_PATH/templates/base.html"; then
    echo -e "${GREEN}✓${NC} templates/base.html - Tailwind CDN still included"
else
    echo -e "${YELLOW}⚠${NC} templates/base.html - Tailwind CDN not found"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED - Ready for testing!${NC}"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Next steps:"
    echo "  1. Start the Flask app: python main.py"
    echo "  2. Open browser: http://localhost:5000"
    echo "  3. Clear cache (Ctrl+Shift+Delete) and hard refresh (Ctrl+Shift+R)"
    echo "  4. Open DevTools (F12) to verify CSS/font files load correctly"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $ERRORS CHECK(S) FAILED - Please review${NC}"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    exit 1
fi
