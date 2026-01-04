from .Auth import router as auth_router
from .City import router as city_router
from .CropYear import router as crop_year_router
from .Factory import router as factory_router
from .Farmer import router as farmer_router
from .MeasureUnit import router as measure_unit_router
from .PaymentReason import router as payment_reason_router
from .Pesticide import router as pesticide_router
from .Product import router as product_router
from .Provinces import router as provinces_router
from .Village import router as village_router
from .User import router as user_router
from .Seed import router as seed_router
from .ProductPrice import router as product_price_router
from .PurityPrice import router as purity_price_router

__all__ = [
    "auth_router",
    "city_router",
    "crop_year_router",
    "factory_router",
    "farmer_router",
    "measure_unit_router",
    "payment_reason_router",
    "pesticide_router",
    "product_router",
    "provinces_router",
    "village_router",
    "user_router",
    "seed_router",
    "product_price_router",
    "purity_price_router",
    "Farmer"
]