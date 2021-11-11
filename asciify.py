import geopandas as gpd
import time

def asciify(gdf, inside_symbol="#", outside_symbol=" ", width=100, crs=4326):

    # PREPARE DATA
    gdf = gdf.to_crs(crs)
    gdf['char'] = inside_symbol
    
    
    # FORMAT ASCII EXTENT
    # get geometrical extents
    minx, miny, maxx, maxy = gdf.total_bounds
    x_extent = maxx - minx
    y_extent = maxy - miny

    # define ascii max size
    maxchars = width
    # space between rows = about 2x character space
    row_space = 2

    # account for higher rowspace
    ratio = (x_extent / y_extent) * row_space
    # line length
    ncols = maxchars
    # number of rows
    nrows = int(maxchars / ratio)

    
    # GENERATE A GEOMETRICAL POINT FOR EACH ASCII CHARACTER
    # axes as iterable lists
    y_axis_i = list(range(nrows))
    x_axis_i = list(range(ncols))

    # x and y Distance between points
    x_step = x_extent/ncols
    y_step = y_extent/nrows

    # generate points
    points = gpd.GeoDataFrame()

    count = 0

    # loop rows
    for iy in y_axis_i:
        
        # y coord
        y_coord = maxy - y_step * iy

        # loop cols
        for ix in x_axis_i:
            x_coord = minx + x_step * ix

            # add to gdf
            points.at[count, "x_coord"] = x_coord
            points.at[count, "y_coord"] = y_coord

            # gdf index
            count = count + 1

    # create geometries
    points["geometry"] = gpd.points_from_xy(points["x_coord"], points["y_coord"])
    points = points.set_crs(epsg=crs)


    # ASSIGN ASCII CHARACTER TO EACH POINT
    # sjoin the inside_symbol
    points = points.sjoin(gdf, how='left')
    # assign the outside_symbol where data doesn't overlap
    points['char'] = points['char'].fillna(outside_symbol)

    
    # FORMAT DATA FROM GEOMETRIES TO ASCII
    # rows as groups
    row_grouped = points.sort_values('x_coord').groupby("y_coord")

    # list for rows
    rows = []
    
    # Format row strings
    for key, group in row_grouped:
        row_list = group["char"].tolist()
        row_str = "".join(map(str, row_list))
        rows.append(row_str)
        
    # print ascii output
    for r in reversed(rows):
        print(r)
        time.sleep(0.05)






