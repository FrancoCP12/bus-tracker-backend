
from sqlalchemy.orm import Session
from app.api.route import GeoJson
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_GeomFromText
from sqlalchemy import func, and_
from app.models.bus_stop import BusStop
from app.models.bus import Bus
import json

def toGeoJson(geojson: GeoJson, session: Session):
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

