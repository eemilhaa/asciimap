import geopandas as gpd
import time

def asciify(gdf, inside_symbol="#", outside_symbol=" ", width=100, crs=4326):

    # PREPARE DATA
    gdf = gdf.to_crs(crs)
    gdf["char"] = inside_symbol
    
    
    # FORMAT ASCII EXTENT
    # get geometrical extents
    minx, miny, maxx, maxy = gdf.total_bounds
    x_extent = maxx - minx
    y_extent = maxy - miny

    # space between rows = about 2x character space
    row_space = 2

    # account for higher rowspace
    ratio = (x_extent / y_extent) * row_space
    # number of rows
    nrows = int(width / ratio)

    
    # GENERATE A GEOMETRICAL POINT FOR EACH ASCII CHARACTER
    # axes as iterable lists
    y_axis_i = list(range(nrows))
    x_axis_i = list(range(width))

    # x and y Distance between points
    x_step = x_extent/width
    y_step = y_extent/nrows

    # generate points
    points = gpd.GeoDataFrame()

    # count to use as index
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
    points = points.sjoin(gdf, how="left")
    # assign the outside_symbol where data doesn"t overlap
    points["char"] = points["char"].fillna(outside_symbol)

    
    # FORMAT DATA FROM GEOMETRIES TO ASCII
    # rows as groups
    row_grouped = points.sort_values("x_coord").groupby("y_coord")

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
        time.sleep(0.03)
        

        
        
        
# Demo script       
if __name__ == "__main__":
    import mapclassify
    
    print("\nRunning asciimap demo with natural earth data...")
    world = gpd.read_file("./example-data/ne_50m_admin_0_countries.zip")
    
    input("\n>> git Press enter to progress")
    input("\n>> Asciify the entire data set:")
    asciify(gdf=world)
    
    input("\n>> Use a different map projection:")
    asciify(gdf=world, crs=3035)
    
    input("\n>> Asciify a single country, customize symbols and ascii size:")
    finland = world.loc[world["NAME_EN"] == "Finland"]
    asciify(
        gdf=finland,
        inside_symbol=" ",
        outside_symbol="_",
        width=40,
        crs=3067
    )
    
    input("\n>> Another example:")
    iceland = world.loc[world["NAME_EN"] == "Iceland"]
    asciify(iceland, "#", "~", 80, 5638)
    
    print("\nThe symbol assignment can be as complex as you like.")
    input("\n>> For example, assign symbols based on first letters of country names:")
    asciify(
        gdf=world,
        inside_symbol=world["NAME_EN"].str[0],
        width=140
    )
    
    input("\n>> How about an ascii choropleth map?")
    # classify data
    column = "POP_EST"
    bins = mapclassify.NaturalBreaks(world[column], k=5).bins
    
    # Assign symbols using the bins
    for i, r in world.iterrows():
        if world[column][i] <= bins[0]:
            world.at[i, "custom_char"] = "."
        elif world[column][i] <= bins[1]:
            world.at[i, "custom_char"] = ":"
        elif world[column][i] <= bins[2]:
            world.at[i, "custom_char"] = "i"
        elif world[column][i] <= bins[3]:
            world.at[i, "custom_char"] = "I"
        elif world[column][i] <= bins[4]:
            world.at[i, "custom_char"] = "#"

    asciify(
        gdf=world,
        inside_symbol=world["custom_char"].str[0],
        width=140
    )
    
    print("\n\nPopulation:")
    print(f".  =  {world[column].min()} - {str(bins[0])[0:-2]}")
    print(f":  =  {str(bins[0])[0:-2]} - {str(bins[1])[0:-2]}")
    print(f"i  =  {str(bins[1])[0:-2]} - {str(bins[2])[0:-2]}")
    print(f"I  =  {str(bins[2])[0:-2]} - {str(bins[3])[0:-2]}")
    print(f"#  =  {str(bins[3])[0:-2]} - {str(bins[4])[0:-2]}\n\n")






