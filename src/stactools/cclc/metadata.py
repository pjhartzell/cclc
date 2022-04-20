import os.path
from typing import Optional

import rasterio
from rasterio.warp import transform_geom
from shapely.geometry import box, mapping, shape
from stactools.core.io import ReadHrefModifier


class Metadata:
    """Class for accessing Item metadata from a COG."""

    def __init__(self,
                 href: str,
                 read_href_modifier: Optional[ReadHrefModifier] = None):
        if read_href_modifier:
            modified_href = read_href_modifier(href)
        else:
            modified_href = href
        with rasterio.open(modified_href) as dataset:
            self.source_crs = dataset.crs
            self.source_bbox = dataset.bounds
            self.source_geometry = mapping(box(*self.source_bbox))
            self.source_shape = dataset.shape
            self.source_transform = list(dataset.transform)[0:6]

        self.href = href

    @property
    def geometry(self):
        return transform_geom(self.source_crs, "EPSG:4326",
                              self.source_geometry)

    @property
    def bbox(self):
        return list(shape(self.geometry).bounds)

    @property
    def id(self):
        return os.path.splitext(os.path.basename(self.href))[0]

    @property
    def proj_properties(self):
        properties = {
            "epsg": None,
            "wkt2": self.source_crs.to_wkt(),
            "shape": self.source_shape,
            "transform": self.source_transform
        }
        return properties
