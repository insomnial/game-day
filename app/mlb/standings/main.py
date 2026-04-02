import requests, json, os, datetime

## Gets the standings for the passed-in date.
def _GetDate(pulldate : datetime) -> dict:

    return

## Gets the standings for the current day.
def GetToday() -> dict:
    return _GetDate(datetime.datetime.today())
