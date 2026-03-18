import os
from django.core.files.images import get_image_dimensions
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

@deconstructible
class ImageValidator:
    def __init__(self,
                 max_size_mb=5,
                 min_width=200,
                 min_height=200,
                 max_width=4000,
                 max_height=4000,
                 allowed_extensions=None):

        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.allowed_extensions = allowed_extensions or ['.jpg', '.jpeg', '.png']

    def __call__(self, image):
        self.validate_extension(image)
        self.validate_size(image)
        self.validate_dimensions(image)

    def validate_extension(self, image):
        extension = os.path.splitext(image.name)[1].lower()
        if extension not in self.allowed_extensions:
            raise ValidationError(
                _(f'Unsupported file extension. Allowed: {", ".join(self.allowed_extensions)}')
            )

    def validate_size(self, image):
        if image.size > self.max_size_bytes:
            size_mb = image.size / (1024 * 1024)
            raise ValidationError(
                _(f'Image size cannot exceed {self.max_size_bytes / (1024 * 1024):.0f}MB. '
                  f'Current size: {size_mb:.2f}MB')
            )

    def validate_dimensions(self, image):
        try:
            width, height = get_image_dimensions(image)

            if width < self.min_width or height < self.min_height:
                raise ValidationError(
                    _(f'Image dimensions must be at least {self.min_width}x{self.min_height}px. '
                      f'Current: {width}x{height}px')
                )

            if width > self.max_width or height > self.max_height:
                raise ValidationError(
                    _(f'Image dimensions cannot exceed {self.max_width}x{self.max_height}px. '
                      f'Current: {width}x{height}px')
                )

        except (AttributeError, TypeError, OSError):
            raise ValidationError(_('Invalid image file'))