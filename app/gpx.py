import gpxpy
import gpxpy.gpx
from app.datafeeds import polyline_to_coords


def route_to_gpx(route):
    gpx = gpxpy.gpx.GPX()
    gpx.name = route.title
    gpx.creator = 'RideTime'
    gpx.description = 'This is a cycling route file as GPX, generated from RideTime'

    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name = route.title
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    route_coords = polyline_to_coords(route.polyline)

    # Create points:
    for coords in route_coords:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(longitude=coords[0], latitude=coords[1]))

    return gpx.to_xml()
