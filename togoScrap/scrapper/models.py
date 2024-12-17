from django.db import models
from django.core.exceptions import ValidationError

def validate_file_extension_cruise_line(value):
    valid_extensions = ['.xlsx']
    if not value.name.endswith(tuple(valid_extensions)):
        raise ValidationError('Unsupported file extension. please upload .xlsx file')
    
# Create your models here.
class CruiseLineFile(models.Model):
    
    FILE_TYPE_CHOICES = [
        ('custom_search', 'Custom Search'),
        ('interline', 'Interline'),
        ('cruise_line', 'Cruise Line')
    ]

    file = models.FileField(upload_to='cruise_line', 
                            validators=[validate_file_extension_cruise_line],
                            null=False, blank=False)
    type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, null=False, blank=False, unique=True)
    
    def __str__(self):
        return self.type
    class Meta:
        unique_together = ['file', 'type']


# def validate_file_extension_region_mapping(value):
#     valid_extensions = ['.json']  # Add '.xlsx' if needed
#     if not value.name.endswith(tuple(valid_extensions)):
#         raise ValidationError('Unsupported file extension. Please upload a .json file.')
    
class RegionMapping(models.Model):
    
    name = models.CharField(max_length=50, choices=[('region_file', 'Region File')],
                            null=False, blank=False, default='region_file', unique=True)
    file = models.FileField(
        upload_to='region',
        validators=[validate_file_extension_cruise_line],
        null=False,
        blank=False
    )
    class Meta:
        unique_together = ['file', 'name']