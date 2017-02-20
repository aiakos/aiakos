#!/usr/bin/env python
import os
import sys

sys.path.append("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_client_django.settings")

from django.core.management import execute_from_command_line

execute_from_command_line(sys.argv)
