from django.contrib import admin
from .models import CruiseLineFile, RegionMapping
from django.utils.safestring import mark_safe
from django.templatetags.static import static

# Register your models here.
class RegionMappingAdmin(admin.ModelAdmin):
    # Customize the form to include the download link
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Add a "Download Sample File" link next to the 'file' field
        if 'file' in form.base_fields:
            # Adjust the file path to use a valid static URL
            file = RegionMapping.objects.first()
            
            if file:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                sample_file_url = file.file.url
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",sample_file_url)
            else:
                print(">>>>>>>>>>>>>>>")
                sample_file_url = static('scrapper/cruise_lines.xlsx')
              # Adjust path based on your static file location
            form.base_fields['file'].help_text = mark_safe(
                f'<a href="{sample_file_url}" download style="color: blue; text-decoration: underline;">Download Sample File</a>'
            )
        
        return form


# Register the model with the custom admin
admin.site.register(RegionMapping, RegionMappingAdmin)
admin.site.register(CruiseLineFile)
