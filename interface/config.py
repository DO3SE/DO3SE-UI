import os, sys

# Use Windows-specific paths if on Windows, otherwise use standard UNIX paths
if os.name == 'nt':
    settings_dir = os.path.join(os.environ['APPDATA'], '.do3se')
else:
    settings_dir = os.path.join(os.environ['HOME'], '.do3se')

# Create the settings directory and copy default data to it if it doesn't exist
if not os.path.exists(settings_dir):
    os.mkdir(settings_dir)

# Testing - print out the paths
if __name__ == "__main__":
    print settings_dir
