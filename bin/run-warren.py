#!/usr/bin/env python

import sys

# These are plugged in by the install process:
PATH_OVERRIDE = None
DEFAULT_SHARE_PATH = None

if PATH_OVERRIDE is not None and PATH_OVERRIDE not in sys.path:
    sys.path.append(PATH_OVERRIDE)

if __name__ == "__main__":
    import warren.runner
    sys.exit(warren.runner.main())
