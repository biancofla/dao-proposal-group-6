from django.shortcuts import render

def index(request):
    return render(request, "home.html")

def create_poll(request):
    return render(request, "new-poll.html")

def vote(request):
    app_id = request.GET.get("appid", "")
    return render(
        request, 
        "vote.html",
        {
            "app_id": app_id
        }
    )

def results(request):
    app_id = request.GET.get("appid", "")
    return render(
        request, 
        "results.html",
        {
            "app_id": app_id
        }
    )