
from app.models.route import Route
from sqlalchemy.orm import Session
from app.api.route import GeoJson
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_GeomFromText
from sqlalchemy import func, and_
from app.models.bus_stop import BusStop
from app.models.bus import Bus
import json

def toGeoJson(geojson: GeoJson, session: Session, bus_id: int):
    data = json.loads(geojson.geojson)
    features = data.get('features', [])
   
    ruta_data = next((f for f in features if f['properties'].get('type') == 'route'), None)
    geom_ruta_shapely = shape(ruta_data['geometry'])
    new_route = Route(position=f"SRID=4326;{geom_ruta_shapely.wkt}")
    
    session.add(new_route)
    session.flush() 

    for f in features:
        if f['properties'].get('type') == 'bus_stop':
            geom_parada = shape(f['geometry'])
            point_wkt = f"SRID=4326;{geom_parada.wkt}"

            existing_stop = session.query(BusStop).filter(
                func.ST_DWithin(
                    func.cast(BusStop.position, Geography),
                    func.cast(func.ST_GeomFromText(point_wkt, 4326), Geography),
                    15 
                )
            ).first()

            if existing_stop:
                new_route.stops.append(existing_stop)
            else:
                nueva_parada = BusStop(position=point_wkt)
                session.add(nueva_parada)
                new_route.stops.append(nueva_parada)

    new_bus = session.query(Bus).filter(Bus.id_bus == bus_id).first()
    new_bus.id_route = new_route.id_route 
    session.commit()
    return {"message": "Ruta y paradas procesadas correctamente"}

def get_bus_stop(user_lat: float, user_lon: float, session: Session):
    user_point = f"SRID=4326;POINT({user_lon} {user_lat})"

    stops = session.query(BusStop).filter(
        func.ST_DWithin(
            func.cast(BusStop.position,Geography),
            func.cast(func.ST_GeomFromText(user_point, 4326), Geography),
            500)
        ).all()
    return stops

def next_bus_stop(bus_id, bus_lat, bus_lon, session: Session):
    bus_point = f"SRID=4326;POINT({bus_lon} {bus_lat})"

    bus_stop = session.query(BusStop)\
        .join(Bus, and_(BusStop.id_route == Bus.id_route, Bus.id_bus == bus_id))\
        .filter(
                T_LineLocatePoint(Route.position, bus_point) < 
                ST_LineLocatePoint(Route.position, BusStop.position))\
        .order_by(ST_LineLocatePoint(Route.position, BusStop.position))\
        .first()
        
    return bus_stop

def get_buses_by_busStop(stop_id: int, session: Session)-> list[int]:
    buses_id = session.query(Bus.id_bus).filter(and_(Bus.id_route == BusStop.id_route, BusStop.id_bus_stop == stop_id)).all()
    return buses_id