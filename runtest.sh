#!/bin/bash

# this is what starts an interactive shell within your container
docker run -ti --rm --volumes-from "odoo.atherm" docker/atherm /bin/bash
