# Create your views here.
from models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

def index(request):
    return render_to_response("index.html", {})

def routes(request):
    context = RequestContext(request, {
        'routes': Route.objects.all()
    })
    return render_to_response("routes.html", context)

def route(request, alias):
    route = get_object_or_404(Route, alias=alias)
    routeDetails = RouteDetail.objects.filter(route=route).order_by('serial')
    context = RequestContext(request, {
        'route': route,
        'routeDetails': routeDetails
    })
    return render_to_response("route.html", context)

def areas(request):
    context = RequestContext(request, {
        'areas': Area.objects.all()
    })
    return render_to_response("areas.html", context)    

def area(request, name):
    area = get_object_or_404(Area, name=name)
    stops = Stop.objects.filter(area=area).order_by('name')
    context = RequestContext(request, {
        'area': area,
        'stops': stops
    })
    return render_to_response("area.html", context)


def editstops(request):
    context = RequestContext(request, {})
    return render_to_response("editstops.html", context)


def stats(request):
    total_stops_left = Stop.objects.filter(point=None).count()
    areas = []
    for a in Area.objects.all():
        stops = Stop.objects.filter(area=a)
        d = {
            'area': a,
            #'area_name': a.name,
            'total_stops': stops.count(),
            'remaining_stops': stops.filter(point=None).count()
        }
        areas.append(d)
    routes = []
    for r in Route.objects.all():
        stops = Stop.objects.filter(routedetail__route=r)
        d = {
            'route': r,
            #'route_name': r.name,
            'total_stops': stops.count(),
            'remaining_stops': stops.filter(point=None).count()
        }
        routes.append(d)
    return render_to_response("stats.html", {
        'total_stops_left': total_stops_left,
        'areas': areas,
        'routes': routes
    })

