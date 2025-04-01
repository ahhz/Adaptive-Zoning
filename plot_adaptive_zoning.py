import geopandas as gpd

import numpy as np
from shapely.geometry import Point, box, Polygon
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi


def plot_agg_voronoi(centroids,agg, ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    # To make sure that all centroids have a corresponding polygon, create four additional points at a 
    # substantial distance from the study areas

    # work out the bounding box, use geopandas function so first put data in geodataframe with shapely points

    geometry = [Point(p[0],p[1]) for p in centroids]

    # create the index column to maintain the order of points
    n = len(agg)
    gdf_points = gpd.GeoDataFrame(data ={'index': range(n), 'cluster':agg}, geometry=geometry)
    xmin, ymin, xmax, ymax = gdf_points.total_bounds;
    
    # "substantial" is 5 x the bounding box lenght, width
    factor = 5
    dx = (xmax-xmin) * factor;
    dy = (ymax-ymin) * factor;

    # create the extended point set centroid + helpers, also place in numpy array
    helpers = [(xmin - dx, ymin - dy), (xmax + dx, ymin - dy), 
               (xmax + dx, ymax + dy), (xmin - dx, ymax + dy)]
    extended_points = np.array(centroids + helpers)

    # create the Voronoi diagram and extract the regions
    vor = Voronoi(extended_points, qhull_options='Qbb Qc Qx');
    regions = [vor.regions[vor.point_region[i]] for i in range(n)] # Get regions in original point order.
   
    # Convert scipy polygons to shapely polygons
    make_polygon = lambda region: Polygon([vor.vertices[i] for i in region])
    is_valid_region = lambda region: -1 not in region and len(region) > 0
    polygons = [make_polygon(region) for region in regions if is_valid_region(region)]

    # for displaying at a small buffer around the original bounding box, so points are not on the edge of the figure
    small_margin = 0.01
    bounding_box_plus = box(xmin - small_margin * dx, ymin - small_margin * dy, 
                            xmax + small_margin * dx, ymax + small_margin * dy)

    # polygons to dataframe and clip to bounding box
    # create the index column to maintain the order of polygons
    gdf_polygons = gpd.GeoDataFrame(data={'index': range(n), 'cluster': agg} , geometry=polygons).clip(bounding_box_plus)
    
    # merge polygons by their cluster
    gdf_polygons = gdf_polygons.dissolve(by="cluster")
    
    # plot the zones
    gdf_polygons.boundary.plot(ax=ax)
    
    #plot the points
    gdf_points.plot(column='cluster', ax=ax, legend=None, markersize=10, cmap='tab20')  
    
    return ax
