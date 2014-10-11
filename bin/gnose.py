#!/usr/bin/env python
"""Utility for executing gevent enabled code.

This fixes an issue with threading getting initialized by nose
before monkey patching for genent occurs. No modification to
nose execution is made.
"""
from gevent import monkey
monkey.patch_all()

import nose

nose.run()
