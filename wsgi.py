#!/usr/bin/env python3

import os
from mizu import app

if __name__ == "__main__":
    app.run(host=app.config['IP'], port=app.config['PORT'], threaded=False)

application = app

