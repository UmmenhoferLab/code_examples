import numpy as np
import copy
import matplotlib.path

def switch_lon_range(lon, neg_to_pos=True):
    """
    Convert longitudes from: [-180,180) to [0,360) and vice versa.
    If neg_to_pos:
        [-180,180) => [0,360)
    else:
        [0,360) => [-180,180)
    """
    lon_ = deepcopy(lon)
    if neg_to_pos:
        lon_[lon_ < 0] = lon_[lon_ < 0] + 360
    else:
        lon_[lon_ > 180] = lon_[lon_ > 180] - 360
    return lon_


def makeMask(vertices, lat, lon, crosses_pm=False):
    """Function returns a mask with with 1s representing the area inside of vertices
    'vertices' is an Nx2 array, representing boundaries of a region.
    'lat' and 'lon' are length-N arrays  
    'cross_pm' is a boolean indicating whether vertices cross the prime meridian"""

    lon_ = copy.deepcopy(lon)
    vertices_ = copy.deepcopy(vertices)

    ### Handle case where region outline crosses prime meridian
    if crosses_pm:
        lon_ = switch_lon_range(lon, neg_to_pos=False)
        vertices_[:, :1] = switch_lon_range(vertices[:, :1], neg_to_pos=False)

    # create 2-D grid from lat/lon coords
    lon_lat_grid = np.meshgrid(lon_, lat)

    # next, get pairs of lon/lat
    t = zip(lon_lat_grid[0].flatten(), lon_lat_grid[1].flatten())

    # convert back to array
    t = np.array(list(t))  # convert to array

    # convert vertices into a matplotlib Path
    path = matplotlib.path.Path(vertices_)
    mask = path.contains_points(t).reshape(len(lat), len(lon))  # create mask
    mask = mask.astype(float)

    # Convert to xr.DataArray
    coords = {"latitude": lat, "longitude": lon}
    dims = ["latitude", "longitude"]
    return xr.DataArray(mask[None, ...], coords=coords, dims=dims)
