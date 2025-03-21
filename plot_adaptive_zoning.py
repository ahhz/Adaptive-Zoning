import geopandas as gpd
from shapely.geometry import Point, box, Polygon
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import numpy as np

def map_to_n_clusters(n, zone_tree, reclass = True):
    def get_cluster(index):
        p = zone_tree.get_parent(index)
        if p != None and p < zone_tree.get_size() - n - 1:
            return get_cluster(p)
        return p if not reclass else p - (zone_tree.get_size() - n - 1)

    return [get_cluster(index) for index in range(zone_tree.get_num_leafs())]

def map_to_given_clusters(given, zone_tree):
    reclass_consecutive = dict([(v,i) for i,v in enumerate(given)])

    def get_cluster(index):
        if index in given: return reclass_consecutive[index]
        return get_cluster(zone_tree.get_parent(index))

    return [get_cluster(index) for index in range(zone_tree.get_num_leafs())]

def plot_agg_voronoi(agg, ax, points):
    n = len(agg)
    gdf_points = gpd.GeoDataFrame(data = {"index":range(n),"cluster":agg}, geometry=[Point(p[0],p[1]) for p in points])
    xmin, ymin, xmax, ymax = gdf_points.total_bounds;
    factor = 5
    dx = (xmax-xmin)*factor;
    dy = (ymax-ymin)*factor;
    extra_points = points + [(xmin-dx,ymin-dy), (xmax+dx,ymin-dy), (xmax+dx, ymax+dy),(xmin-dx, ymax+dy)]
    bounding_box_plus = box(xmin-0.01*dx, ymin-0.01*dy, xmax+0.01*dx, ymax +0.01*dy)
    vor = Voronoi(np.array(extra_points), qhull_options='Qbb Qc Qx');
    regions = [vor.regions[vor.point_region[i]] for i in range(len(points))] # Get regions in original point order.
    polygons = []
    for region in regions:
        if -1 not in region and len(region) > 0: # Ensure valid region.
            polygon = Polygon([vor.vertices[i] for i in region])
            polygons.append(polygon)
    
    gdf_polygons = gpd.GeoDataFrame(data = {"index":range(n),"cluster":agg} , geometry=polygons).clip(bounding_box_plus)
    gdf_polygons = gdf_polygons.dissolve(by="cluster")
    gdf_polygons.boundary.plot(ax=ax)
    gdf_points.plot(column='cluster', ax=ax, legend=None, markersize=10, cmap='tab20')
   
def plot_cluster_voronoi(n, zone_tree, points, ax):
    agg = map_to_n_clusters(n,zone_tree)
    plot_agg_voronoi(agg, ax, points)

def plot_neighbourhood_voronoi(neighbourhood, zone_tree, points,ax):
    agg = map_to_given_clusters(neighbourhood,zone_tree)
    plot_agg_voronoi(agg, ax, points)
