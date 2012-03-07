from models import *
from ox.django.shortcuts import get_object_or_404_json, render_to_json_response
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
import re

def route(request, slug):
    srid = int(request.GET.get("srid", 4326))
    route = get_object_or_404_json(Route, slug=slug)
    stops = [r.stop.get_geojson(srid=srid) for r in RouteDetail.objects.filter(route=route)]
    return render_to_json_response({
        'route': route.get_dict(),
        'stops': {
            'type': 'FeatureCollection',
            'features': stops
        }
    })

def area(request, slug):
    srid = int(request.GET.get("srid", 4326))
    area = get_object_or_404_json(Area, slug=slug)
    stops = [stop.get_geojson(srid=srid) for stop in Stop.objects.filter(area=area)]
    return render_to_json_response({
        'area': area.get_dict(),
        'stops': { 
            'type': 'FeatureCollection',
            'features': stops
        }
    })

def routes(request):    
    q = request.GET.get("q", "")
    in_regex = re.compile(r'(\d{1,3})') # used to extract the route number string out of the query string - for eg, gets "21" from "21Ltd"
    match = re.findall(in_regex, q)
    if match:
        route_no = match[0]
    else:
        route_no = ''
    ret = []
    if route_no != '':
        out_regex = re.compile(r'.*(\D|\A)%s(\D|\Z).*' % route_no) # used for, for eg. to filter out '210Ltd' when user searches for '21'. Checks for non-digit or start of string, followed by route_no, followed by non-digit or end of string
        qset = Route.objects.filter(alias__icontains=route_no)
        for route in qset:
            if re.match(out_regex, route.alias):             
                ret.append(route.alias)        
    else:
        qset = Route.objects.all()
        for route in qset:
            ret.append(route.alias)
#    routes = [route.alias for route in qset]
    return render_to_json_response(ret)


def areas(request):
    q = request.GET.get("q", "")
    if q != '':
        qset = Area.objects.find_approximate(q, 0.33)
    else:
        qset = Area.objects.all()
    areas = [area.slug for area in qset]
    return render_to_json_response(areas)


def stops(request):
    q = request.GET.get("q", "")
    if q != '':
        qset = Stop.objects.find_approximate(q, 0.33)
    else:
        qset = Stop.objects.all()
    srid = int(request.GET.get("srid", 4326))   
    return render_to_json_response({
        'type': 'FeatureCollection',
        'features': [stop.get_geojson(srid=srid) for stop in qset]
    })
   

@csrf_exempt
def stop(request, slug):
    srid = int(request.GET.get("srid", 4326))
    if request.POST and request.POST.has_key('geojson'):
        if not slug:
            stop = Stop() #FIXME: should this return an error instead?
        else:
            stop = get_object_or_404_json(Stop, slug=slug)
        geojson = json.loads(request.POST['geojson'])
        return render_to_json_response(stop.from_geojson(geojson, srid))
    else:
        stop = get_object_or_404_json(Stop, slug=slug)        
        return render_to_json_response(stop.get_geojson(srid=srid)) #FIXME: please don't repeat this code, its retarded.
