import geopandas as gpd

grid_fp = 'C:/Users/shubh/Downloads/mallapur_bound/Selected_Mandal_grid.shp'
centerline_fp = 'C:/Users/shubh/Downloads/mallapur_farms_forcenterline/mallapur_farms_forcenterline.shp'
grid_file = gpd.read_file(grid_fp)

centerline_file = gpd.read_file(centerline_fp)
grid_file = grid_file.to_crs("EPSG:3857")

for index, grid in  grid_file.iterrows():
    clip_part = centerline_file.clip(grid.geometry)
    outfile = centerline_fp[:-4] + f'_{index}.shp'
    clip_part.to_file(outfile)