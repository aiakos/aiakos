#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aiakos.settings")

from django.core.management import execute_from_command_line  # isort:skip

execute_from_command_line(sys.argv)
