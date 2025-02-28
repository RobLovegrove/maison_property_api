#!/bin/bash
black --line-length 79 app/ tests/ 

flake8 app/ tests/