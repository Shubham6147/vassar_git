import rasterio
from rasterio.enums import Resampling




image = r"F:\DEM_Extraction\SHP-TO-DEM\n19_e085_3arc_v2_gt_mul_1.5_m_nig.tif"

upscale_factor = 1.3

with rasterio.open(image) as dataset:

    # resample data to target shape using upscale_factor
    data = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset.height * upscale_factor),
            int(dataset.width * upscale_factor)
        ),
        resampling=Resampling.nearest
    )

    print('Shape before resample:', dataset.shape)
    print('Shape after resample:', data.shape[1:])

    # scale image transform
    dst_transform = dataset.transform * dataset.transform.scale(
        (dataset.width / data.shape[-1]),
        (dataset.height / data.shape[-2])
    )

    print('Transform before resample:\n', dataset.transform, '\n')
    print('Transform after resample:\n', dst_transform)

    ## Write outputs
    ##set properties for output
    dst_kwargs = dataset.meta.copy()
    dst_kwargs.update(
    {

        "transform": dst_transform,
        "width": data.shape[-1],
        "height": data.shape[-2],
        "nodata": 0,
    }
    )

    with rasterio.open(r"F:\DEM_Extraction\SHP-TO-DEM\n19_e085_3arc_v2_gt_mul_1.5_m_nig_2.tif", "w", **dst_kwargs) as dst:
    # iterate through bands
        for i in range(data.shape[0]):
              dst.write(data[i], i+1)