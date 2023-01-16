#!/usr/bin/env python3
"""
MongoDB Operations with Python using pymongo insert
"""


def insert_school(mongo_collection, **kwargs):
    """ Insert a document into MongoDB """
    return mongo_collection.insert(kwargs)
