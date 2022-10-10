from venv import create
from django.urls import path
from .views import (
    index,
    create_poll,
    vote,
    results
)

urlpatterns = [
    path(""       , index      , name="home"       ),
    path("new"    , create_poll, name="create-poll"),
    path("vote"   , vote       , name="vote"       ),
    path("results", results    , name="results"    ),
]
