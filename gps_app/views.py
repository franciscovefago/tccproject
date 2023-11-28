from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from datetime import date, time, datetime
from .models import User, GPSDevice, Movement, PreviousLocation, Cercado
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.gis.geos import Point
import json
import folium
from django.shortcuts import render
import geocoder
from django.views.decorators.csrf import csrf_exempt

def is_inside(gps_device):
    lat = gps_device.current_latitude
    lon = gps_device.current_longitude

    cercado = gps_device.cercado

    # Check if the GPS device is inside the cercado polygon
    num_points = 4
    inside = False

    for i in range(num_points):
        j = (i + 1) % num_points

        # Extract the latitude and longitude coordinates of each vertex
        lat_i, lon_i = getattr(cercado, f'lat{i+1}'), getattr(cercado, f'lon{i+1}')
        lat_j, lon_j = getattr(cercado, f'lat{j+1}'), getattr(cercado, f'lon{j+1}')

        if (
            ((lat_i > lat) != (lat_j > lat)) and
            (lon < (lon_j - lon_i) * (lat - lat_i) / (lat_j - lat_i) + lon_i)
        ):
            inside = not inside

    return inside


def home(request):
    notify = False
    inside = True
    try:
        gps_data = GPSDevice.objects.get(id=1)
    except:
        gps_data=None

    total_distance = 0
    previous_point = None

    today = date.today()

    coordinates = PreviousLocation.objects.filter(
        Q(timestamp__year=today.year) &
        Q(timestamp__month=today.month) &
        Q(timestamp__day=today.day)).order_by('timestamp')

    for coordinate in coordinates:
        current_point = Point(float(coordinate.longitude), float(coordinate.latitude))

        if previous_point:
            distance = previous_point.distance(current_point)
            total_distance += distance

        previous_point = current_point

    month_distance = 0
    previous_point = None

    month_coordinates = PreviousLocation.objects.filter(
        Q(timestamp__year=today.year) &
        Q(timestamp__month=today.month) &
        Q(timestamp__day=today.day)).order_by('timestamp')

    for coordinate in month_coordinates:
        current_point = Point(float(coordinate.longitude), float(coordinate.latitude))

        if previous_point:
            distance = previous_point.distance(current_point)
            month_distance += distance

        previous_point = current_point

    print('Distance today: '+str(total_distance))
    print('Distance this month: '+str(month_distance))
  
    if gps_data is not None:
        print("Cercado: ")
        print(gps_data.cercado)


    movements = Movement.objects.filter(
        Q(start_time__year=today.year) &
        Q(start_time__month=today.month) &
        Q(start_time__day=today.day)).order_by('start_time')


    if gps_data is not None:
        if gps_data.current_speed > 5:
            notify = True

        if gps_data.cercado:
            inside = is_inside(gps_data)

    todays_day = datetime.today().day

    avg_distance = month_distance/todays_day

    if gps_data.cercado is not None:
        ponto1 = (gps_data.cercado.lat1, gps_data.cercado.lon1) 
        ponto2 = (gps_data.cercado.lat2, gps_data.cercado.lon2) 
        ponto3 = (gps_data.cercado.lat3, gps_data.cercado.lon3) 
        ponto4 = (gps_data.cercado.lat4, gps_data.cercado.lon4)

        m = folium.Map(location=ponto1, zoom_start=15)
    
        Previous = PreviousLocation.objects.all()

        marker_locations = []
        for Previou in Previous:
            folium.Marker(location=[Previou.latitude, Previou.longitude], popup='').add_to(m)
            marker_locations.append([Previou.latitude, Previou.longitude])

        folium.PolyLine(locations=marker_locations, color='blue').add_to(m)

        
        folium.Polygon(locations=[ponto1, ponto2, ponto3, ponto4, ponto1], color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(m)

        mapa_html = m._repr_html_()
    else:
        g = geocoder.ip('me')
        latitude, longitude = g.latlng
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        mapa_html = m._repr_html_()
    
    return render(request, 'index.html', {'mapa_html': mapa_html, 'gps_data': gps_data, 'todays_distance': total_distance, 'months_distance': month_distance, 'gps_locations_today': coordinates, 'total_movements': len(movements), 'notify': notify, 'avg_distance': avg_distance, 'inside': inside, 'map': m})

def login(request):
    return render(request, 'login.html')

def profile(request):
    return render(request, 'profile.html')

def register(request):
    return render(request, 'register.html')

def table(request):
    return render(request, 'table.html')

@api_view(['POST'])
#@csrf_exempt
def gps_coordinates(request):
    print(request.data)
    
    latitude = request.data.get('latitude')
    longitude = request.data.get("longitude")
    altitude = request.data.get('altitude')
    speed = request.data.get('speed')
    counter = int(request.data.get('counter'))
    
    # margem de erro do gps
    speed = float(speed)
    if speed < 0.99:
        speed = 0

    print(latitude)
    print(longitude)

    print(counter)
 
    try:
        gps_data = GPSDevice.objects.get(id=1)
        print(gps_data)
        print("Updating GPSDevice's data...")
        # Every 10 new received information, a new data of location is saved.
        if counter % 10 == 0:
            try:
                new_past_location = PreviousLocation(latitude = latitude, longitude = longitude, timestamp = gps_data.last_updated, device_id = gps_data)
                new_past_location.save()
                print('New past location added to database.')
            except Exception as e:
                print(e)
                print("Could not register previous location.")
    except:
        gps_data = GPSDevice(id=1, last_updated= datetime.now(), name='Nameless GPS', current_latitude=latitude, current_longitude=longitude, current_altitude=altitude, current_speed=speed)
        print("Device Not Found. Creating new on Database.")
        
    today = date.today()
    current_point = Point(float(longitude), float(latitude))

    coordinates = PreviousLocation.objects.filter(
        Q(timestamp__year=today.year) &
        Q(timestamp__month=today.month) &
        Q(timestamp__day=today.day)).order_by('timestamp')

    if coordinates:
        distance_traveled = current_point.distance(Point(float(coordinates[0].longitude), float(coordinates[0].latitude)))
        print('Distance from last time: '+str(distance_traveled))
        if distance_traveled > 0.5 and speed >= 1:
            print('MOVEMENT DETECTED')
            new_movement = Movement(device_id=gps_data.id, first_location=coordinates[0], final_latitude=latitude, final_longitude=longitude, start_time=coordinates[0].timestamp, finish_time=date.today())
            new_movement.save()    

    gps_data.current_latitude = latitude
    gps_data.current_longitude = longitude
    gps_data.current_altitude = altitude
    gps_data.current_speed = speed

    gps_data.save()

    return Response({'message': 'GPS coordinates saved'})

def gps_data_list(request):
    try:
        gps_data = GPSDevice.objects.get(id=1)
    except:
        nothing_found={'name': 'nothingfound', 'current_latitude':0, 'current_longitude':0}
        return render(request, 'index.html', {'gps_data': nothing_found})
        
    return render(request, 'gps_data_list.html', {'gps_data': gps_data})

def update_device_name(request):
    device = GPSDevice.objects.get(id=1)
    if device:
        new_name = request.POST.get('name')
        device.name = new_name
        device.save()

    return redirect('/')

def update_cercado_to_device(request):
    cercadoid = request.GET.get('cercadoid')
    deviceid = request.GET.get('deviceid')

    device = GPSDevice.objects.get(id=deviceid)
    cercado = Cercado.objects.get(id=cercadoid)
    device.cercado = cercado
    
    device.save()
    return redirect('/mapa')

def config_cercado(request):
    device = GPSDevice.objects.get(id=1)

    id = request.POST.get('id')

    name = request.POST.get('name')

    lat1 = float(request.POST.get('lat1'))
    lon1 = float(request.POST.get('lon1'))

    lat2 = float(request.POST.get('lat2'))
    lon2 = float(request.POST.get('lon2'))
    
    lat3 = float(request.POST.get('lat3'))
    lon3 = float(request.POST.get('lon3'))
    
    lat4 = float(request.POST.get('lat4'))
    lon4 = float(request.POST.get('lon4'))
  
    if id is not None and id.isdigit():
        cercado_data = Cercado(id=id, name=name, lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2, lat3=lat3, lon3=lon3, lat4=lat4, lon4=lon4)
    else:
        cercado_data = Cercado(name=name, lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2, lat3=lat3, lon3=lon3, lat4=lat4, lon4=lon4)
    
    cercado_data.save()

    device.cercado = cercado_data
    
    device.save()

    return redirect('/mapa')

def remove_cercado(request):
    cercadoid = request.GET.get('cercadoid')

    cercado = Cercado.objects.get(id=cercadoid)

    cercado.delete()

    return redirect('/mapa')

def mapa(request):
    try:
        gps_data = GPSDevice.objects.get(id=1)
    except:
        gps_data={'name': 'nothingfound', 'current_latitude':0, 'current_longitude':0}
  
    g = geocoder.ip('me')
    latitude, longitude = g.latlng

    if gps_data.cercado and gps_data.cercado.lat1 is not None:
        latitude = gps_data.cercado.lat1
    
    if gps_data.cercado and gps_data.cercado.lon1 is not None:
        longitude = gps_data.cercado.lon1

    cercados = Cercado.objects.exclude(id=gps_data.cercado.id).order_by('name')

    mapas = []

    for cercado in cercados:
        ponto1 = (cercado.lat1, cercado.lon1) 
        ponto2 = (cercado.lat2, cercado.lon2) 
        ponto3 = (cercado.lat3, cercado.lon3) 
        ponto4 = (cercado.lat4, cercado.lon4)

        # Criar um mapa centrado em uma das coordenadas (por exemplo, S�o Paulo)
        mapa_cercado = folium.Map(location=ponto1, zoom_start=14)

        # Adicionar um pol�gono (quadrado) ao mapa usando os quatro pontos
        folium.Polygon(locations=[ponto1, ponto2, ponto3, ponto4, ponto1], color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(mapa_cercado)

        # # Adicionar marcadores para os quatro pontos
        # folium.Marker(location=ponto1, popup='Ponto 1').add_to(mapa_cercado)
        # folium.Marker(location=ponto2, popup='Ponto 2').add_to(mapa_cercado)
        # folium.Marker(location=ponto3, popup='Ponto 3').add_to(mapa_cercado)
        # folium.Marker(location=ponto4, popup='Ponto 4').add_to(mapa_cercado)
        
        mapas.append({'cercado': cercado, 'mapa': mapa_cercado._repr_html_()})

    return render(request, 'mapa.html', {'gps_data': gps_data,'mapas': mapas, 'cercados': cercados, 'form': '', 'latitude':latitude, 'longitude': longitude })


def example(request):
    CERCADO_UFSC = Cercado.objects.get(id=1)

    # coordenadas dentro da UFSC
    gps_data = {'name': "The Example GPS", 'current_latitude': -28.95149057705809, 'current_longitude': -49.467360307796156, 'current_altitude': 15.4785, 'current_speed': 0.0, 'cercado': CERCADO_UFSC}    

    #   coordenadas fora da UFSC
    # gps_data = {'name': "The Example GPS", 'current_latitude': -28.949480733, 'current_longitude': -49.466650288, 'current_altitude': 15.4785, 'current_speed': 3.0, 'cercado': CERCADO_UFSC}

    notify = False
    inside = True

    lat = gps_data['current_latitude']
    lon = gps_data['current_longitude']

    # Check if the GPS device is inside the cercado polygon
    num_points = 4
    inside = False

    for i in range(num_points):
        j = (i + 1) % num_points

        # Extract the latitude and longitude coordinates of each vertex
        lat_i, lon_i = float(getattr(CERCADO_UFSC, f'lat{i+1}')), float(getattr(CERCADO_UFSC, f'lon{i+1}'))
        lat_j, lon_j = float(getattr(CERCADO_UFSC, f'lat{j+1}')), float(getattr(CERCADO_UFSC, f'lon{j+1}'))

        if (
            ((lat_i > lat) != (lat_j > lat)) and
            (lon < (lon_j - lon_i) * (lat - lat_i) / (lat_j - lat_i) + lon_i)
        ):
            inside = not inside
    
    distances_today = [0.0, 0.0, 4.5, 1.3, 5.2, 1.2, 3.3, 0.0]

    movements = 4

    month_distance = 128.22

    todays_day = datetime.today().day

    avg_distance = month_distance/todays_day

    total_distance = 0
    for distance in distances_today:
        total_distance += distance
    
    print('Distance per 3 hour: '+str(distances_today))

    chart_labels = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
    chart_data = {
        "type": "line",
        "data": {
            "labels": chart_labels,
            "datasets": [{
                "label": "Earnings",
                "fill": True,
                "data": distances_today,
                "backgroundColor": "rgba(78, 115, 223, 0.05)",
                "borderColor": "rgba(78, 115, 223, 1)"
            }]
        },
        "options": {
            "maintainAspectRatio": False,
            "legend": {
                "display": False,
                "labels": {
                    "fontStyle": "normal"
                }
            },
            "title": {
                "fontStyle": "normal"
            },
            "scales": {
                "xAxes": [{
                    "gridLines": {
                        "color": "rgb(234, 236, 244)",
                        "zeroLineColor": "rgb(234, 236, 244)",
                        "drawBorder": False,
                        "drawTicks": False,
                        "borderDash": ["2"],
                        "zeroLineBorderDash": ["2"],
                        "drawOnChartArea": False
                    },
                    "ticks": {
                        "fontColor": "#858796",
                        "fontStyle": "normal",
                        "padding": 20
                    }
                }],
                "yAxes": [{
                    "gridLines": {
                        "color": "rgb(234, 236, 244)",
                        "zeroLineColor": "rgb(234, 236, 244)",
                        "drawBorder": False,
                        "drawTicks": False,
                        "borderDash": ["2"],
                        "zeroLineBorderDash": ["2"]
                    },
                    "ticks": {
                        "fontColor": "#858796",
                        "fontStyle": "normal",
                        "padding": 20
                    }
                }]
            }
        }
    }

    if gps_data['current_speed'] > 1:
        notify = True

    chart_data_json = json.dumps(chart_data)

    return render(request, 'example.html', {'gps_data': 
    gps_data, 'todays_distance': total_distance, 'months_distance': month_distance, 'total_movements': movements, 'distance_per_time': distances_today, 'chart_data': chart_data_json, 'notify': notify, 'avg_distance': avg_distance, 'inside': inside})