from django.http import HttpResponse
from points.models import Point, Map


def create(request):
    map = Map(name="Map 1")
    map.save()

    point = Point(map=map)
    point.save()

    return HttpResponse("Map and Point created successfully!")

def list_maps_and_points(request):
    maps = Map.objects.all()

    response = "Maps:\n"
    for map in maps:
        response += f"- {map.id}: {map.name}\n"
        points = Point.objects.filter(map=map)
        response += "  Points:\n"
        for point in points:
            response += f"  - {point.id}\n"
    return HttpResponse(response)

