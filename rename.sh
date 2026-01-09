#!/bin/bash

#===============================================================================
# Media Renamer - Interactive Launcher
# An interactive wrapper for file_renamer.sh
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENAMER="$SCRIPT_DIR/file_renamer.sh"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if file_renamer.sh exists
if [ ! -f "$RENAMER" ]; then
    echo -e "${RED}Error: file_renamer.sh not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Clear screen and show header
clear
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    Media Renamer                              ║${NC}"
echo -e "${CYAN}║         Rename your movies, TV shows, and music              ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Select mode
echo -e "${GREEN}What would you like to rename?${NC}"
echo ""
echo "  [1] Movies"
echo "  [2] TV Shows"
echo "  [3] Music"
echo "  [4] Auto-detect (all media types)"
echo "  [5] Exit"
echo ""
echo -e "Select option [1-5]: "
read -r mode_choice

case "$mode_choice" in
    1)
        MODE="movies"
        NEEDS_API_KEY="true"
        echo -e "${CYAN}Mode: Movies${NC}"
        ;;
    2)
        MODE="tv"
        NEEDS_API_KEY="true"
        echo -e "${CYAN}Mode: TV Shows${NC}"
        ;;
    3)
        MODE="music"
        NEEDS_API_KEY="false"
        echo -e "${CYAN}Mode: Music${NC}"
        ;;
    4)
        MODE="auto"
        NEEDS_API_KEY="true"
        echo -e "${CYAN}Mode: Auto-detect${NC}"
        ;;
    5|"")
        echo -e "${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option. Exiting.${NC}"
        exit 1
        ;;
esac
echo ""

# Check for API key (only needed for movies/TV)
if [ "$NEEDS_API_KEY" = "true" ] && [ -z "$TMDB_API_KEY" ]; then
    echo -e "${YELLOW}TMDB API key required for movies/TV.${NC}"
    echo -e "Enter your TMDB API key (get one free at themoviedb.org):"
    read -r api_key
    if [ -z "$api_key" ]; then
        echo -e "${RED}API key required for this mode.${NC}"
        exit 1
    fi
    export TMDB_API_KEY="$api_key"
    echo ""
fi

# Get directory
echo -e "${GREEN}Enter the directory containing your media files:${NC}"
echo -e "(Press Enter for current directory)"
read -r target_dir

if [ -z "$target_dir" ]; then
    target_dir="."
fi

if [ ! -d "$target_dir" ]; then
    echo -e "${RED}Error: Directory '$target_dir' does not exist${NC}"
    exit 1
fi
echo ""

# Dry run option
echo -e "${GREEN}Would you like to preview changes first? (dry run)${NC}"
echo -e "[Y/n]: "
read -r dry_run_choice

DRY_RUN=""
if [ "$dry_run_choice" != "n" ] && [ "$dry_run_choice" != "N" ]; then
    DRY_RUN="-d"
    echo -e "${YELLOW}Dry run enabled - no files will be renamed${NC}"
fi
echo ""

# Logging option
echo -e "${GREEN}Enable logging?${NC}"
echo -e "[y/N]: "
read -r log_choice

LOG_OPT=""
if [ "$log_choice" = "y" ] || [ "$log_choice" = "Y" ]; then
    echo -e "Enter log filename (default: rename.log): "
    read -r log_file
    if [ -z "$log_file" ]; then
        log_file="rename.log"
    fi
    LOG_OPT="-l $log_file"
    echo -e "${CYAN}Logging to: $log_file${NC}"
fi
echo ""

# Confirm and run
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Ready to start!${NC}"
echo -e "  Directory: $target_dir"
echo -e "  Mode: $MODE"
[ -n "$DRY_RUN" ] && echo -e "  Dry run: Yes"
[ -n "$LOG_OPT" ] && echo -e "  Log file: $log_file"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Press Enter to continue or Ctrl+C to cancel..."
read -r

# Run the renamer
"$RENAMER" -m "$MODE" $DRY_RUN $LOG_OPT "$target_dir"
