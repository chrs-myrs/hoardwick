#!/bin/bash
# Zenity wrapper for sudo password prompts
# Usage: SUDO_ASKPASS=/path/to/zenity-askpass.sh sudo -A command

zenity --password --title="sudo password required"
